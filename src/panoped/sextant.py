"""Ordinary frozen-query localization calibration; not an SO(3) network.

The target geometry is release L1 (a zero-roll local angular rectangle).
Identity histories, confidence and detector support are not changed here.
"""
import math
import torch
from torch import nn


def _validate(parameters):
    if parameters.shape[-1]!=7 or not torch.isfinite(parameters).all():
        raise ValueError('Finite native parameter vectors required')
    if not torch.allclose(parameters[...,:3].norm(dim=-1),torch.ones_like(parameters[...,0]),atol=2e-6,rtol=0):
        raise ValueError('Unit centre rays required')
    if not torch.all(parameters[...,5]==1) or not torch.all(parameters[...,6]==0):
        raise ValueError('This control has only zero-roll release targets')
    ext=parameters[...,3:5].exp()
    if torch.any(ext<=0) or torch.any(ext>ext.new_tensor([2*math.pi,math.pi])):
        raise ValueError('Invalid angular extent')


def encode_correction(base,target):
    _validate(base);_validate(target)
    if base.shape!=target.shape:raise ValueError('Aligned base/target shapes required')
    lon0=torch.atan2(base[...,0],base[...,2]);lon1=torch.atan2(target[...,0],target[...,2])
    lat0=torch.atan2(base[...,1],base[...,[0,2]].norm(dim=-1));lat1=torch.atan2(target[...,1],target[...,[0,2]].norm(dim=-1))
    dlon=torch.atan2((lon1-lon0).sin(),(lon1-lon0).cos())
    return torch.cat((torch.stack((dlon,lat1-lat0),-1)/base[...,3:5].exp(),target[...,3:5]-base[...,3:5]),-1)


def decode_correction(base,delta):
    _validate(base)
    if delta.shape!=base.shape[:-1]+(4,) or not torch.isfinite(delta).all():raise ValueError('Aligned finite residuals required')
    lon=torch.atan2(base[...,0],base[...,2]);lat=torch.atan2(base[...,1],base[...,[0,2]].norm(dim=-1))
    shift=delta[...,:2]*base[...,3:5].exp()
    dlat=torch.minimum(torch.maximum(shift[...,1],-math.pi/2-lat),math.pi/2-lat)
    # A latitude rotation followed by world-y longitude rotation. At zero,
    # preserve the original ray bit-for-bit; no round-trip trig reconstruction.
    north=torch.stack((-lat.sin()*lon.sin(),lat.cos(),-lat.sin()*lon.cos()),-1)
    v=base[...,:3]*dlat.cos()[...,None]+north*dlat.sin()[...,None]
    c,s=shift[...,0].cos(),shift[...,0].sin()
    center=torch.stack((c*v[...,0]+s*v[...,2],v[...,1],-s*v[...,0]+c*v[...,2]),-1)
    limits=base.new_tensor([math.log(2*math.pi),math.log(math.pi)])
    logs=torch.minimum((base[...,3:5]+delta[...,2:]).clamp_min(math.log(torch.finfo(base.dtype).tiny)),limits)
    return torch.cat((center,logs,base[...,5:]),-1)


class LocalizationCalibrator(nn.Module):
    def __init__(self):
        super().__init__();self.norm=nn.LayerNorm(256);self.net=nn.Sequential(nn.Linear(262,128),nn.GELU(),nn.Linear(128,4))
        nn.init.zeros_(self.net[-1].weight);nn.init.zeros_(self.net[-1].bias)

    def forward(self,query,base,confidence,*,box_only=False):
        if query.ndim!=2 or query.shape!=(len(base),256) or confidence.shape!=(len(base),):raise ValueError('Aligned frozen queries required')
        if not torch.isfinite(query).all() or not torch.isfinite(confidence).all():raise ValueError('Nonfinite observation')
        _validate(base)
        q=torch.zeros_like(query) if box_only else self.norm(query)
        return self.net(torch.cat((q,base[:,:5],confidence[:,None]),-1))

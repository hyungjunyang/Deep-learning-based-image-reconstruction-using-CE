#----------------------------------------
# VAE agent for preserving geological realism 
#-----------------------------------------

import torch
from torch.autograd import Variable
import numpy as np
import sys
from model.vae import * 

# compute VAE loss 
def getVaeProxLoss( m, m_initial, lambda_vae, model ): 
    recon_input, mu, logvar = model(m)
    loss, _, _ = loss_fn(recon_input, m, mu, logvar)
    loss += 0.5 * ((m_initial - m) ** 2 ).sum()/lambda_vae
    return loss

# VAE agent
def vaeGeologyPrior(m, vae_case, channel_params, simul_params, pnp_params):
    ngx = simul_params["ngx"]
    ngy = simul_params["ngy"]
    lperm = channel_params["lperm"]
    hperm = channel_params["hperm"]
    lambda_vae = pnp_params["vae_reg"] 
    m = m.reshape(1, 1, ngx, ngy)
    m = torch.from_numpy(m)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if (vae_case == 1): 
        trained_params = torch.load('model_zoo/vae_case1.torch', map_location = device)
        model = VAE(vae_case = 1, image_channels = 1).to(device)
    if (vae_case == 2): 
        trained_params = torch.load('model_zoo/vae_case2.torch', map_location = device)
        model = VAE(vae_case = 2, image_channels = 1).to(device)
    m = m.to(device, torch.float)
    model.load_state_dict(trained_params)
    m_initial = m
    m = torch.autograd.Variable(m)
    loss = getVaeProxLoss( m, m_initial, lambda_vae, model )
    m.requires_grad = True 
    while True:
        alpha = 0.1
        loss_old = loss
        loss = getVaeProxLoss( m, m_initial, lambda_vae, model )
        grad = torch.autograd.grad(loss, m)
        while True:
            m_new = m - alpha*grad[0]
            m_new[m_new < 0] = 0
            m_new[m_new > 1] = 1
            loss = getVaeProxLoss( m_new, m_initial, lambda_vae, model )
            if loss >= loss_old:
                alpha = 0.5 * alpha
            if alpha < 0.01 or loss <= loss_old:
                break
        m = m_new
        if loss >= loss_old:
            break
    m_out = m.detach().numpy() 
    m_out = m_out.reshape(ngx*ngy,1)
    return m_out

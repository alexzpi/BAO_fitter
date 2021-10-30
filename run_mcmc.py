import numpy as np
import scipy.interpolate as itp
import scipy.integrate as integrate
import scipy.optimize as op
import sys
import pickle
from ps_template import *
from multipoles import *
from chi_squared import *
from truncate_covariance import *
import zeus
from zeus import ChainManager

# read parameters from file
params = sys.argv[1]
with open(params, 'r') as file:
    lines = file.readlines()
label = lines[0].split()[1]
#mul_path = lines[1].split()[1]
#cov_path = lines[2].split()[1]
out_path = lines[3].split()[2]
ps_lin_path = lines[4].split()[3]
sigma_r = float(lines[5].split()[1])
iso = bool(int(lines[6].split()[2]))
space = lines[7].split()[1]
#q_min = float(lines[8].split()[1]) # q means either s or k
#q_max = float(lines[9].split()[1])
n_mu = int(lines[10].split()[1])
bb_exp = list(map(int, lines[11].split(sep=': ')[1].split(sep=', ')))

# Linear template and mu
linear_template = np.loadtxt(ps_lin_path, unpack=True)
mu = np.linspace(0.001, 1., n_mu)

# Open dictionary
dict_path = out_path + label.lower() + '.dict'
with open(dict_path, 'rb') as file:
        dictionary = pickle.load(file)
data = dictionary['multipoles']
cov_matrix = dictionary['covariance']
cov_inv = np.linalg.inv(cov_matrix)
bf = dictionary['best_fit_values']
sigmas = [bf['Sigma_par'], bf['Sigma_per'], bf['Sigma_fog']]
print('Read file: ' + dict_path)

# Run ZEUS sampler
ndim = 4 # Number of parameters/dimensions 
nwalkers = 2*ndim # Number of walkers to use. It should be at least twice the number of dimensions.
nsteps = 4000 # Number of steps/iterations.
nchains = 2
bi = 0.3 # Burn-in

# Initial positions of the walkers.
start_b = 0.2 * np.random.randn(nwalkers)[:,None] + 1.5
start_beta = 0.5 * np.random.rand(nwalkers)[:,None] + 1
start_alpha_par = 0.1 * np.random.rand(nwalkers)[:, None] + 1
start_alpha_per = 0.1 * np.random.rand(nwalkers)[:,None] + 1
start = np.concatenate((start_b, start_beta, start_alpha_par, start_alpha_per), axis=1)

with ChainManager(nchains) as cm:
    rank = cm.get_rank

    sampler = zeus.EnsembleSampler(nwalkers, ndim, logpost, args=[data, cov_inv, linear_template, mu, sigma_r, iso, bb_exp, sigmas, space], pool=cm.get_pool) # Initialise the sampler
    sampler.run_mcmc(start, nsteps) # Run sampling
    sampler.summary # Print summary diagnostics

    chains = sampler.get_chain(flat=False, thin=1)
    n_bi = int(len(chains)*bi)
    chains = chains[n_bi:]
    chains_path = out_path + 'chains_' + str(rank) + '.npy'
    np.save(chains_path, chains)
    print('Saved file: ' + chains_path)

#with open(summary_path, 'w') as file:
#    file.write(f'Number of Generations: {nsteps}\n')
#    file.write(f'Number of Parameters: {ndim}\n')
#    file.write(f'Number of Walkers: {nwalkers}\n')
#    file.write(f'Number of Tuning Generationss: {len(sampler.scale_factor)}\n')
#    file.write(f'Scale Factor: {sampler.scale_factor[-1]}\n')
#    file.write(f'Mean Integrated Autocorrelation Time: {np.mean(sampler.act)}\n')
#    file.write(f'Effective Sample Size: {sampler.ess}\n')
#    file.write(f'Number of Log Probability Evaluations: {sampler.ncall}\n')
#    file.write(f'Effective Samples per Log Probability Evaluation: {sampler.efficiency}')

# # save results
# chain = np.reshape(chains, (len(chains)*10, 4))
# alpha_cov = np.cov(chain[:, 2:].T)
# b_median = np.percentile(chain[:, 0], 50)
# beta_median = np.percentile(chain[:, 1], 50)
# alpha_par_median = np.percentile(chain[:, 2], 50)
# alpha_per_median = np.percentile(chain[:, 3], 50)
# alpha_par_sigma = np.sqrt(alpha_cov[0,0])
# alpha_per_sigma = np.sqrt(alpha_cov[1,1])
# corr = alpha_cov[0,1]/(alpha_par_sigma*alpha_per_sigma)

# dict_path = '/global/homes/a/alexpzfz/alexdesi/bao_fitting/results/'+label.lower()+'.dict'
# with open(dict_path, 'rb') as file:
#     data_dict = pickle.load(file)
# chi2 = data_dict['best_fit'].fun
# dof = 2*len(data[0]) - 13

# results_path = '/global/homes/a/alexpzfz/alexdesi/bao_fitting/results/submission/'+label.lower()+'_bestfit.txt'
# with open(results_path, 'w+') as file:
#     file.write('median_alpha_par, median_alpha_perp, sigma_alpha_par, sigma_alpha_perp, corr_alpha_par_perp, bf_chi2, dof, b, beta\n')
#     file.write(str(alpha_par_median)+" ")
#     file.write(str(alpha_per_median)+" ")
#     file.write(str(alpha_par_sigma)+" ")
#     file.write(str(alpha_per_sigma)+" ")
#     file.write(str(corr)+" ")
#     file.write(str(chi2)+" ")
#     file.write(str(dof)+" ")
#     file.write(str(b_median)+" ")
#     file.write(str(beta_median))
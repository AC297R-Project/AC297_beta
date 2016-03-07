import numpy as np
import matplotlib.pyplot as plt
from get_beta import get_beta

# Demonstrate how get_beta works using some noisy synthetic data
X = np.arange(1000)
Y = 2*X + np.random.normal(scale=30, size=1000)
r = get_beta(Y, X)
alphas, betas = r[0], r[1]
plt.figure(figsize=(8,6));
plt.plot(X[60:], alphas + X[60:]*betas, color='k', label='Beta estimate');
plt.plot(X, Y, color='r', alpha=0.5, label='Data')
plt.legend(loc=0);
plt.xlim(0, 1000);
plt.ylim(0, 2000);
plt.show();

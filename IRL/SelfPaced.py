# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 17:06:55 2018

@author: thoma
"""
import numpy as np
import scipy.optimize as opt
from IRL import IRL

#Self paced

class Self_Paced(IRL):
    
    def __init__(self,f,K0,eps,mu,model=None,constraint='hard'):
        self.f = f #class created by laetitia, comme GIRL par exemple, objet IRL
        self.K = K0 
        self.eps=eps
        self.mu = mu
        # params correspond to the ws in the paper.
        if self.model is None:
            self.params = self.zero()
        else:
            self.params = self.model.get_params() # this may be subject to change
        self.constraint = constraint
        #self.data=data
            
        self.w = self.f.reward.params #w is the weight of our model, see GIRL example
    
    def zero(self):
        self.f.zero()
        
    def reg(self,w):
        #for regularisation
        return 0
        
    def fit(self,trajs):
        start=True #for first iteration
        self.v = - np.ones(len(trajs)) #start
        v0 = np.random.rand(len(trajs))
        old_v = self.v
        
        ws = []
        
        loss = []
        while((self.v == np.ones(len(trajs))).all()): #find a termination condition perhaps double while (alternative search, and then decrement)
            
            #Alternative search strategy
            while(start == True or not((old_v == self.v).all())):
                #minimising for v
# =============================================================================
#                 result_v = opt.minimize(self.objective_v, v0, constraints=self.v_constraints)
#                 if not result_v.success:
#                     print(result_v.message)
#                     print(result_v)
#                 self.v = result_v.x
# =============================================================================
                
                losses = self.f.loss(trajs)
                print(losses)
                #second method use dirac
                old_v=self.v
                self.v = np.where(losses < 1/self.K,1,0)
                
                #minimising for w
                result_w = opt.minimize(self.objective_w, self.w)
                if not result_w.success:
                    print(result_w.message)
                    print(result_w)
                self.w = result_w.x
                self.f.reward.set_params(self.w)
            
            ws.append(self.w)
            self.K=self.mu * self.K
        
        return ws
    
    def objective_w(self,w,trajs):
        return(np.dot(self.v, self.f.loss(w,trajs))+self.reg(w) ) #le reste est independant de w donc pas besoin de calculer
        
    def objective_v(self,v,trajs):
        return(np.dot(v,self.f.loss(trajs)) - np.sum(v)/self.K) #think about a way to only calculate objective if v is 1
        
    def objective(self,inputs,trajs):
        w,v = inputs
        return(self.reg(w) + v*self.f.objective(self.w) - np.sum(v)/self.K)
        
    
        
   
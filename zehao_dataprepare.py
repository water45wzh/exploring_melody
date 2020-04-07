#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import shutil
import math
import time
import json


# In[5]:


class Note():
    def __init__(self, pitch, duration, punit=1, dunit=100):
        self.pitch = pitch/punit
        self.duration = duration/dunit

class STC(list):
    def __init__(self, *elements, punit=1, dunit=1):
        super(STC, self).__init__(elements)
        self.punit = punit
        self.dunit = dunit
    
    def append(self, note):
        return STC(*self, note, punit = self.punit, dunit = self.dunit)
    
    def MCG(self):
        d = 0
        s = 0
        for n in self:
            s += n.pitch*n.duration
            d += n.duration
        return s/d
    
    def GMD_series(self):
        if len(self)<2:
            return [0]
        def LMD(n1, n2):
            p1 = max(0,n1.pitch-n2.pitch)
            p2 = max(0,n2.pitch-n1.pitch)
            d1 = n1.duration/(n1.duration+n2.duration)*math.exp(1/n1.duration+n2.duration)
            d2 = n2.duration/(n1.duration+n2.duration)*math.exp(1/n1.duration+n2.duration)
            lmd = math.fabs(p1*d1 - p2*d2)
            return lmd
        s = []
        for i in range(len(self)-1):
            s.append(LMD(self[i], self[i+1]))
        return s
    
    def GMD(self, norm='inf', reduction='sum'):
        gmds = self.GMD_series()
        if norm == 'inf':
            if reduction == 'sum':
                return max(gmds)
            elif reduction == 'mean':
                return max(gmds)/len(gmds)
        elif norm == 1:
            if reduction == 'sum':
                return sum(gmds)
            elif reduction == 'mean':
                return sum(gmds)/len(gmds)
        else:
            print('Invalid norm/reduction!')
            assert False
            
    def get_stc_rhythm(self):
        l = []
        for n in self:
            l.append(n.duration)
        return l
    
    def delta_timeseries(self):
        num = len(self)
        ts = self.get_stc_rhythm()
        if num < 2:
            return [0]
        l = []
        for i in range(num-1):
            if (ts[i]+ts[i+1]) > 0:
                s = math.fabs((ts[i+1]-ts[i])*2/(ts[i]+ts[i+1]))
            else:
                s = 0
            l.append(s)
        return l
    
    def delta2_timeseries(self):
        num = len(self)
        ts = self.get_stc_rhythm()
        if num < 3:
            return [0]
        l = []
        for i in range(num-1):
            if (ts[i]+ts[i+1]) > 0:
                s = math.fabs((ts[i+1]-ts[i])*2/(ts[i]+ts[i+1]))
            else:
                s = 0
            l.append(s)
        ll = []
        for i in range(num-2):
            if (l[i]+l[i+1]) > 0:
                s = math.fabs((l[i+1]-l[i])*2/(l[i]+l[i+1]))
            else:
                s = 0
            ll.append(s)
        return ll
    
    def PV_series(self, is_show=False):
        pvs = self.delta_timeseries()
        if is_show:
            plt.plot(pvs)
        return pvs
    
    def PV(self, norm=1, reduction='mean'):
        pvs = self.PV_series()
        if norm == 'inf':
            if reduction == 'sum':
                return max(pvs)
            elif reduction == 'mean':
                return max(pvs)/len(pvs)
        elif norm == 1:
            if reduction == 'sum':
                return sum(pvs)
            elif reduction == 'mean':
                return sum(pvs)/len(pvs)
        else:
            print('Invalid norm/reduction!')
            assert False
    
    def RD_series(self, is_show=False):
        rds = self.delta2_timeseries()
        if is_show:
            plt.plot(rds)
        return rds

    def RD(self, norm=1, reduction='mean'):
        rds = self.RD_series()
        if norm == 'inf':
            if reduction == 'sum':
                return max(rds)
            elif reduction == 'mean':
                return max(rds)/len(rds)
        elif norm == 1:
            if reduction == 'sum':
                return sum(rds)
            elif reduction == 'mean':
                return sum(rds)/len(rds)
        else:
            print('Invalid norm/reduction!')
            assert False   
    
    def get_features(self):
        return [self.MCG(), self.GMD(), self.GMD(norm = 1), 100*self.PV(), 100*self.RD()]


# In[6]:


class Melody():
    def __init__(self, name, events_file, punit=1, dunit=100):    
        events_list = []
        with open(events_file,'r') as f:
            for line in f:
                events_list.append(line.strip('\n'))
        self.events = events_list
        self.name = name
        self.punit = punit
        self.dunit = dunit
    
    def stcwise(self):
        stclist = []
        elist = self.events
        num = len(elist)
        i = 0
        stc = STC(punit = self.punit, dunit = self.dunit)
        while i < num:
            # stc-loop
            k = 1
            while i < num and k==1:
                # in_stc-loop
                if elist[i][:5] == 'pitch' and elist[i][-2:] == 'on':
                    p = int(elist[i][6:-3])
                    j = i+1
                    kk = 1
                    d = 0
                    while j < num and kk == 1:
                        if elist[j][:4] == 'time':
                            d += int(elist[j][5:])
                            j += 1
                        elif elist[j][:5] == 'pitch' and elist[j][-3:] == 'off':
                            i = j+1
                            kk = 0
                        else:
                            j += 1
                    n = Note(p,d,punit = self.punit, dunit = self.dunit)
                    stc = stc.append(n)
                    continue
                elif elist[i][:4] == 'time':
                    i += 1
                    if len(stc) != 0:
                        k = 0
                        stclist.append(stc)
                        stc = STC(punit = self.punit, dunit = self.dunit)
                    break
                else:
                    i += 1
            if len(stc) != 0:
                stclist.append(stc)
        return stclist
    
    def get_stc_features(self):
        l = []
        stclist = self.stcwise()
        for stc in stclist:
            l.append(stc.get_features())
        return l


# In[7]:


path = "./ndatasets/event"
save_path = ".ndatasets/zehao"
# 不知为何 'b' 文件夹下会陷入死循环，所以这里直接把这个文件夹移出得了，之后移出该文件夹中有问题的文件然后当作 feature 预测模型的测试集
ftdt = {}

filesss= os.listdir(path) # abcd
for filess in filesss: 
    if os.path.isdir(path+"/"+filess):
        files = os.listdir(path+"/"+filess) # author's name
        print('Start ' + filess + '!')
        for file in files:
            if os.path.isdir(path+"/"+filess+"/"+file):
                fls = os.listdir(path+"/"+filess+"/"+file) # song's name
                for fl in fls:
                    if os.path.isdir(path+"/"+filess+"/"+file+"/"+fl):
                        fs = os.listdir(path+"/"+filess+"/"+file+"/"+fl) # different format
                        for f in fs:
                            if f[:5] == 'whole':
                                m = Melody(fl, path+"/"+filess+"/"+file+"/"+fl+"/"+f)
                                length = len(m.stcwise())
                                if length > 1:
                                    ft = m.get_stc_features()
                                    #print(fl)
                                    ftfile = open('features.txt', 'w')
                                    ftfile.write(fl + '\n')
                                    ftfile.write(str(ft))
                                    ftdt[fl] = ft
        print('Finish ' + filess + '!')


# In[7]:


len(ftdt)


# In[44]:


dtv =  ftdt.values()
dc = {}
count = 0
for v in ftdt:
    k = ftdt[v]
    ls = 0
    for kk in k:
        if max(kk) > 1000:
            ls = 1
    if ls == 0:
        dc[v] = k
    else:
        count += 1


# In[46]:


jsonfile = './proper_features.json'

with open(jsonfile, 'w') as f:
    json.dump(dc, f)


# In[45]:


len(dc)


# In[ ]:





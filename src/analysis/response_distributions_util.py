import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from stats_utils import *
import pytz, datetime, dateutil




def get_single_motivation(m):
    if len(m.split('|')) == 1:
        return m
    return None

def utc_to_local(dt, timezone):
    utc_dt = pytz.utc.localize(dt, is_dst=None)
    try:
        return  utc_dt.astimezone (pytz.timezone (timezone) )
    except:
        return None

def get_std_err(num_events, num_trials):
    dist =  get_beta_dist(num_events, num_trials, num_samples = 5000)
    ci = bayesian_ci(dist, 95)
    return ci[0] #(ci[1]-ci[0]) / 2

def get_std_err_series(s):
    n = s.sum()
    return s.apply(lambda x: get_std_err(x, n))


def get_lower_std_err(num_events, num_trials):
    dist =  get_beta_dist(num_events, num_trials, num_samples = 5000)
    ci = bayesian_ci(dist, 95)
    return ci[0]
    
def get_lower_std_err_series(s):
    n = s.sum()
    return s.apply(lambda x: get_lower_std_err(x, n))


def get_upper_std_err(num_events, num_trials):
    dist =  get_beta_dist(num_events, num_trials, num_samples = 5000)
    ci = bayesian_ci(dist, 95)
    return ci[1]
    
def get_upper_std_err_series(s):
    n = s.sum()
    return s.apply(lambda x: get_upper_std_err(x, n))

    

def plot_proportion(d, x, hue, title,  xorder = None, dropna_x = True, dropna_hue = True, rotate = False, normx = True):
    
    if dropna_x:
        d = d[d[x] != 'no response']
    else:
        xorder.append('no response')
        
    if dropna_hue:
        d = d[d[hue] != 'no response']
    
    if not normx:
        temp = x
        x = hue
        hue = temp
        
    d_in = pd.DataFrame({'count' : d.groupby( [x, hue] ).size()}).reset_index()
    d_in['err'] = d_in.groupby(hue).transform(get_std_err_series)
    d_in['proportion'] = d_in.groupby(hue).transform(lambda x: x/x.sum())['count']
    
    d_exp = pd.DataFrame()
    counts = d_in.groupby(hue)['count'].sum()
    for i, r in d_in.iterrows():
    
        n = counts[r[hue]]
        n1 = r['count']
        n0  =n - n1
        r_new = r[[x, hue]]
        r_new['in_data'] = 1
        d_exp = d_exp.append([r_new]*n1,ignore_index=True)
        r_new['in_data'] = 0
        d_exp = d_exp.append([r_new]*n0,ignore_index=True)
        
    if not normx:
        temp = x
        x = hue
        hue = temp
        
    fig = sns.barplot(
                x = x,
                y = 'in_data',
                data=d_exp,
                hue = hue,
                order = xorder,
                color = (0.54308344686732579, 0.73391773700714114, 0.85931565621319939)
                )
    plt.ylabel('proportion')
    plt.title(title)
    
    if rotate:
        plt.xticks(rotation=45) 

    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)


def plot_metric_breakdowns(df, metric):

    dims = ['host', 'information depth', 'prior knowledge', 'single motivation']
    
    _ = plt.hist(df[metric])
    plt.figure()

    for i, dim in enumerate(dims): 
        plot_metric(df, dim, metric, rotate = True)
        plt.figure()
        plot_metric(df, dim, metric, estimator =np.median, ci = None, rotate = True)
        plt.figure()
        
    
def plot_metric(d, x, y,
                hue = None,
                title = '',
                xorder = None,
                dropna_x = True,
                dropna_hue = True,
                rotate = False,
                estimator = np.mean, 
                ci = 95, 
                kind  = 'bar', ):
    

    if dropna_x:
        #d = d.dropna(subset=x)
        d = d[d[x] != 'no response']
    else:
        xorder.append('no response')
        
    if hue and dropna_hue:
        #d = d.dropna(subset=hue)
        d = d[d[hue] != 'no response']
        
    if kind == 'bar':
        fig = sns.barplot(
                    x = x,
                    y = y,
                    data=d,
                    hue = hue,
                    order = xorder,
                    color = (0.54308344686732579, 0.73391773700714114, 0.85931565621319939),
                    estimator = estimator,
                    ci = ci
                    )
    else:
        fig = sns.boxplot(
                x = x,
                y = y,
                data=d,
                hue = hue,
                order = xorder,
                color = (0.54308344686732579, 0.73391773700714114, 0.85931565621319939),
                fliersize = 0
                )
    plt.title(title)
    
    if rotate:
        plt.xticks(rotation=45)


def plot_over_time(d, x, xticks, hue, hue_order, figsize, xlim ):
    plt.figure(figsize = figsize)
    d_in = pd.DataFrame({'count' : d.groupby( [x, hue] ).size()}).reset_index()
    d_in['lower_err'] = d_in.groupby(x)['count'].transform(get_lower_std_err_series)
    d_in['upper_err'] = d_in.groupby(x)['count'].transform(get_upper_std_err_series)
    d_in['proportion'] = d_in.groupby(x).transform(lambda x: x/x.sum())['count']
    

    for h in hue_order:
        d_in_h = d_in[d_in[hue] == h]
        plt.errorbar(d_in_h[x].values,
                     d_in_h['proportion'].values,
                     fmt='-o',
                     yerr= [d_in_h['proportion'] - d_in_h['lower_err'] ,d_in_h['upper_err'] - d_in_h['proportion'] ],
                     label = h,
                     alpha = 0.9,
                     linewidth = 1.0,
                     markersize = 5.0
                    )
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel(x)
    plt.xlim(xlim)
    plt.ylabel('proportion')
    plt.xticks(d_in_h[x].values, xticks)


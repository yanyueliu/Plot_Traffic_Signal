# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 22:43:29 2020

@author: Lyy
"""

import pandas as pd
import numpy as np
import re
import random
import matplotlib.patches as patches
import matplotlib.pyplot as plt

class Node(object):
    idcase = {}
    def __init__(self, nid, ntype, x, y):
        self.id = nid
        self.type = ntype
        self.x = x
        self.y = y
        self.link_approach = []
        self.link_exit = []
        Node.idcase[self.id] = self
    
class Link(object):
    idcase = {}
    def __init__(self, lid, from_nd, to_nd, vf, num_of_lanes, w=12, kj=120, qmax=1800, flow_input=200):
        self.id = lid
        self.from_node = from_nd
        self.to_node = to_nd
        self.num_of_lanes = num_of_lanes
        self.vf = vf
        self.w = w
        self.kj = kj
        self.qmax = qmax
        self.flowinput = flow_input
        Link.idcase[self.id] = self
        
class Movement(object):
    idcase = {}
    def __init__(self, gdir, from_link, to_link):
        self.gdirect = gdir # 1 = Left, 2 = Stright, 3 = Right
        self.from_link = from_link
        self.to_link = to_link
        self.move = str(from_link) + ',' + str(to_link)
        self.ratio = None
        Movement.idcase[str(from_link) + ',' + str(to_link)] = self
        
    def getAllMovement():
        df = pd.DataFrame(columns=["Movement", "gdirect", "Corr_Node", "Ratio"])
        index = 0
        temp_df = pd.DataFrame(columns=["Movement", "gdirect", "Corr_Node", "Ratio"])
        from_link = 0
        for key in Movement.idcase:
            if from_link == 0 or from_link == Movement.idcase[key].from_link:
                temp_df.loc[index] = [key, 
                                      Movement.idcase[key].gdirect, 
                                      Node.idcase[Link.idcase[Movement.idcase[key].from_link].to_node].id,
                                      Movement.idcase[key].ratio]
                
                from_link = Movement.idcase[key].from_link
            else:
                temp_df = temp_df.sort_values(by="gdirect")
                df = df.append(temp_df)
                temp_df = pd.DataFrame(columns=["Movement", "gdirect", "Corr_Node", "Ratio"])
                temp_df.loc[index] = [key, 
                                      Movement.idcase[key].gdirect, 
                                      Node.idcase[Link.idcase[Movement.idcase[key].from_link].to_node].id,
                                      Movement.idcase[key].ratio]
                from_link = 0
                
            index += 1
            
        temp_df = temp_df.sort_values(by="gdirect")
        df = df.append(temp_df)       
        df.to_csv("movement.csv")
            
    def getMovementByFromLink(self):
        linkid = self.from_link
        tempList = []
        for key in Movement.idcase:
            if linkid == Movement.idcase[key].from_link:
                tempList.append(Movement.idcase[key])
            else:
                continue
            
        return tempList
    
def readNetwork():
    link_file = pd.read_csv("link.csv")
    node_file = pd.read_csv("node.csv")
    
    for i in range(len(link_file)):
        Link(*list(link_file.iloc[i]))
    
    for j in range(len(node_file)):
        Node(*list(node_file.iloc[j]))
        
    for key in Node.idcase:
        if Node.idcase[key].type == 0:
            for subkey in Link.idcase:
                if Link.idcase[subkey].from_node == Node.idcase[key].id:
                    Node.idcase[key].link_exit.append(Link.idcase[subkey])
                elif Link.idcase[subkey].to_node == Node.idcase[key].id:
                    Node.idcase[key].link_approach.append(Link.idcase[subkey])
                    
def getLength(x,y):
    return np.sqrt(x**2 + y**2)

def getCosine(x1, x2, y1, y2):
    return (x2*x1 + y2*y1) / getLength(x1,y1) / getLength(x2,y2)

def getCrossProduct(va, vb):
    return va[0]*vb[1] - va[1]*vb[0]

def initMovement():
    for key in Node.idcase:
        for app_link in Node.idcase[key].link_approach:
            app_vector = [Node.idcase[app_link.to_node].x - Node.idcase[app_link.from_node].x, 
                              Node.idcase[app_link.to_node].y - Node.idcase[app_link.from_node].y]
            for exit_link in Node.idcase[key].link_exit:
                exit_vector = [Node.idcase[exit_link.to_node].x - Node.idcase[exit_link.from_node].x, 
                              Node.idcase[exit_link.to_node].y - Node.idcase[exit_link.from_node].y]
                
                cosine = getCosine(app_vector[0], exit_vector[0], app_vector[1], exit_vector[1])
                if getCrossProduct(app_vector, exit_vector) > 0:
                    right_flag = 0
                else:
                    right_flag = 1
                
                if -0.707 < cosine <= 0.707 and right_flag:
                    Movement(3, app_link.id, exit_link.id)
                elif 0.707 < cosine <= 1:
                    Movement(2, app_link.id, exit_link.id)
                elif -0.707 < cosine <= 0.707 and not right_flag:
                    Movement(1, app_link.id, exit_link.id)
                    
def getExitLinkByApproachLink(n):
    tempList = []
    for key in Movement.idcase:
        if Movement.idcase[key].from_link == n:
            tempList.append(Movement.idcase[key].to_link)
            
    return tempList
                    
def convertOutput():                    
    df = pd.read_csv("output_valve.csv", index_col=0)
    for key in Node.idcase:
        nd = Node.idcase[key]
        if nd.type == 0:
            temp_df = pd.DataFrame(column=df.columns)
            output_phase = pd.DataFrame()
            for applink in nd.link_approach:
                exitlink_list = getExitLinkByApproachLink(applink)
                for elem in exitlink_list:
                    move = str(applink)+','+str(elem)
                    temp_df.loc[move] = df.loc[move]
                    
            count = 0
            for i in range(len(temp_df.columns)):
                if i < len(temp_df.columns) - 1:
                    b = list(temp_df[temp_df.columns[i]] == temp_df[temp_df.columns[i+1]])
                    if False in b:
                        output_phase
                        count = 0
                    else:
                        count += 1
                        
def getRatio():
    df = pd.read_csv('Zhu_model_flow.csv', index_col=0)
    tot_vol = 0
    for row in df.index:
        m = re.split(r'\D', row)
        move = m[1] + ',' + m[-4]
        if m[1] == m[-4]:
            tot_vol = np.sum(df.loc[row])
        if move in Movement.idcase and tot_vol:
            Movement.idcase[move].ratio = np.sum(df.loc[row]) / tot_vol
            
    ratio = 0
    for key in Movement.idcase:
        if Movement.idcase[key].ratio == None:
            movements = Movement.idcase[key].getMovementByFromLink()
            for i in range(len(movements)):
                if not i:
                    movements[i].ratio = random.uniform(0, 1)
                    ratio += movements[i].ratio
                elif i > 0 and i < len(movements) - 1:
                    movements[i].ratio = random.uniform(0, 1 - ratio)
                    ratio += movements[i].ratio
                else:
                    movements[i].ratio = 1 - ratio
            ratio = 0
            
def plotSignal():
    movedf = pd.read_csv('movement.csv', index_col=1)
    signaldf = pd.read_csv('output_signal.csv')
    signaldf = signaldf.where(signaldf['gdirect'] != 3).dropna()
    movement_list = []
    for i in range(len(signaldf)):
        movement_list.append(str(int(signaldf.iloc[i]['from'])) + ',' + str(int(signaldf.iloc[i]['to'])))
        
    signaldf['movement'] = movement_list
    signaldf = signaldf.set_index('movement')
    
    style = "Simple,tail_width=0.5,head_width=4,head_length=8"
    kw = dict(arrowstyle=style, color="k")
    
    for nd in Node.idcase:
        if Node.idcase[nd].type != 0:
            continue
        
        tempdf = movedf.where(movedf['Corr_Node'] == nd).dropna(subset=['Corr_Node']).where(movedf['gdirect'] != 3).dropna(subset=['Corr_Node'])
        green_phase = {}
        
        theta = signaldf.loc[tempdf.index]['theta'].drop_duplicates().sort_values()
        count = 0
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')
        
        duration = 0
        last_phase = 0
        last_signal_df = pd.DataFrame()
        plotted = {}
        
        for i in range(len(theta)):
            phase = 0
            temp_signal_df = signaldf.loc[tempdf.index]
            temp_signal_df = temp_signal_df.where(temp_signal_df['theta'] == theta[i]).dropna()
            if theta[i] < last_phase:
                # phase += 1
                for j in range(len(last_signal_df)):
                    last_signal_df.iloc[j]['phi'] = last_phase - theta[i]
                
                temp_signal_df = temp_signal_df.append(last_signal_df)
                temp_signal_df = temp_signal_df.sort_values(by=['phi'])
                
                # plotted.pop(last_signal_df.index[j])
            
            for k in range(len(temp_signal_df)):
                if temp_signal_df.index[k] in plotted:
                    phase += 1
                    continue
                duration = theta[i]
                ax.add_patch(
                    patches.Rectangle(
                        (duration, phase * 20), # center
                        temp_signal_df.iloc[k]['phi'], # width
                        10, # height
                        color='g'))
                
                plotted[temp_signal_df.index[k]] = 1
                
                ax.text(duration + 0.55 * temp_signal_df.iloc[k]['phi'], 5 + phase * 20, 
                        str(int(temp_signal_df.iloc[k]['phi'])), color='w', fontsize=12, horizontalalignment='center',
                        verticalalignment='center')
                
                from_node = {'x': Node.idcase[Link.idcase[temp_signal_df.iloc[k]['from']].from_node].x, 
                             'y': Node.idcase[Link.idcase[temp_signal_df.iloc[k]['from']].from_node].y}
                
                to_node = {'x': Node.idcase[Link.idcase[temp_signal_df.iloc[k]['from']].to_node].x, 
                             'y': Node.idcase[Link.idcase[temp_signal_df.iloc[k]['from']].to_node].y}
                
                link_vector = {'x': to_node['x'] - from_node['x'],
                               'y': to_node['y'] - from_node['y']}
                
                cosine = getCosine(link_vector['x'], 0, link_vector['y'], 1)
                cp = getCrossProduct([link_vector['x'], link_vector['y']], [0, 1])
                
                if temp_signal_df.iloc[k]['gdirect'] == 1:
                    if cosine < 0.5 and cosine > -0.5:
                        if cp > 0:
                            ax.add_patch(patches.FancyArrowPatch(
                            (duration - 1 + 0.3 * temp_signal_df.iloc[k]['phi'], 
                             11 + phase * 20),
                            (5 + duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                             18 + phase * 20), connectionstyle="arc3, rad=0.4", **kw))
                        else:
                            ax.add_patch(patches.FancyArrowPatch(
                            (5 + duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                             18 + phase * 20),
                            (duration - 1 + 0.3 * temp_signal_df.iloc[k]['phi'], 
                             11 + phase * 20), connectionstyle="arc3, rad=0.4", **kw))
                    else:
                        if cosine > 0.5:
                            ax.add_patch(patches.FancyArrowPatch(
                            (5 + duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                             11 + phase * 20),
                            (duration - 1 + 0.3 * temp_signal_df.iloc[k]['phi'], 
                             18 + phase * 20), connectionstyle="arc3, rad=0.4", **kw))
                        else:
                            ax.add_patch(patches.FancyArrowPatch(
                            (duration - 1 + 0.3 * temp_signal_df.iloc[k]['phi'], 
                             18 + phase * 20),
                            (5 + duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                             11 + phase * 20), connectionstyle="arc3, rad=0.4", **kw))
                else:
                    if cosine < 0.5 and cosine > -0.5:
                        if cp > 0:
                            ax.add_patch(patches.FancyArrowPatch(
                                (duration + 0.15 * temp_signal_df.iloc[k]['phi'], 
                                 15 + phase * 20),
                                (5 + duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                                 15 + phase * 20), **kw))
                        else:
                            ax.add_patch(patches.FancyArrowPatch(
                                (5 + duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                                 15 + phase * 20),
                                (duration + 0.15 * temp_signal_df.iloc[k]['phi'], 
                                 15 + phase * 20), **kw))
                    else:
                        if cosine > 0.5:
                            ax.add_patch(patches.FancyArrowPatch(
                                (duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                                 10 + phase * 20),
                                (duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                                 20 + phase * 20), **kw))
                        else:
                            ax.add_patch(patches.FancyArrowPatch(
                                (duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                                 20 + phase * 20),
                                (duration + 0.5 * temp_signal_df.iloc[k]['phi'], 
                                 10 + phase * 20), **kw))
                
                if duration != 0:
                    ax.add_patch(patches.Rectangle(
                            (duration + 0.5, phase * 20), # center
                            1, # width
                            10, # height
                            color='y'))
                    
                    ax.add_patch(patches.Rectangle(
                            (duration + 1.5, phase * 20), # center
                            0.5, # width
                            10, # height
                            color='r'))
                    
                ax.add_patch(patches.Rectangle(
                            (duration, 10 + phase * 20), # center
                            temp_signal_df.iloc[k]['phi'], # width
                            9.5, # height
                            fill=False))
                
                phase += 1
                count += 1
                
                ax.autoscale_view(tight=None, scalex=True, scaley=True)
                last_phase = theta[i] + min(temp_signal_df['phi'])
                last_signal_df = temp_signal_df
        
        plt.rcParams['savefig.dpi'] = 400 #图片像素
        plt.rcParams['figure.dpi'] = 400
        plt.savefig('%i' % nd)
    
if __name__ == '__main__':
    random.seed(123)
    readNetwork()
    initMovement()
    # getRatio()
    Movement.getAllMovement()
    plotSignal()
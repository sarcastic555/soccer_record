import redis
import sys
import re
import numpy as np
import matplotlib.pyplot as plt

memberlist=['nakagawa','katayama','arai','tabuchi','ohno','hashimoto','kagata','wada','jinkawa','shimabukuro','tanaka','matsuda','fujikura','takada']
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def initialize():
    global r
    for member in memberlist:
        r.delete(member)
        r.hset(member, 'league-goalnum', 0)
        r.hset(member, 'cup-goalnum', 0)
        r.hset(member, 'training-goalnum', 0)
        r.hset(member, 'league-assistnum', 0)
        r.hset(member, 'cup-assistnum', 0)
        r.hset(member, 'training-assistnum', 0)

#### 得点とアシストの記録 #########
def set_result(type):
    global r
    for info in r.keys("%s*-info"%type):
        print('=================')
        label=r.hget(info,'label').decode('utf-8')
        print (r.hget(info,'opponent').decode('utf-8')) ## これをつけると日本語でも文字化けしない
        scorenum = int(r.hget(info,'myscore').decode('utf-8'))
        ### 得点者の記録
        for i in range(scorenum):
            goal_name=r.lindex('%s-goal'%label,i).decode('utf-8')
            if not (goal_name in memberlist):
                print('%s not found in memberlist'%goal_name)
                sys.exit()
            #print(goal_name)
            goalnum=int(r.hget(goal_name,'%s-goalnum'%type).decode('utf-8'))
            r.hset(goal_name, '%s-goalnum'%type, goalnum+1)
        ### アシスト者の記録
        for i in range(scorenum):
            print(i)
            assist_name=r.lindex('%s-assist'%label,i).decode('utf-8')
            print(assist_name)
            if(assist_name=='None'):
                continue
            if not (assist_name in memberlist):
                print('%s not found in memberlist'%assist_name)
                sys.exit()
            assistnum=int(r.hget(assist_name,'%s-assistnum'%type).decode('utf-8'))
            r.hset(assist_name, '%s-assistnum'%type, assistnum+1)


### 結果の表示
def output_result(type):
    for member in memberlist:
        print(member)
        print(r.hgetall(member))

#r.set('foo', 'bar')
#aho=r.get('foo')

#r.hmset('rect2', {'width':'7.5', 'height':'12.5'})
#aho=r.hgetall('rect2')

#r.rpush('key01', 'A')
#r.rpush('key01', 'B')
#r.rpush('key01', 'C')
#r.rpush('key01', 'D')
#aho=r.lrange('key01', 0, -1)

r.hmset('league1-info', {'label':'league1', 'date':'2018-03-25', 'opponent':'SUGINAMI SC', 'myscore':0, 'opponentscore':1, 'type':'official'})

r.hmset('league2-info', {'label':'league2', 'date':'2018-04-08', 'opponent':'プログレッソ東京', 'myscore':3, 'opponentscore':1, 'type':'official'})
r.lpush('league2-goal', 'arai', 'katayama', 'nakagawa')
r.lpush('league2-assist', 'None', 'None', 'None')

r.hmset('league3-info', {'label':'league3', 'date':'2018-04-22', 'opponent':'FCトリプレッタ', 'myscore':4, 'opponentscore':1, 'type':'official'})
r.lpush('league3-goal', 'tanaka', 'nakagawa', 'wada', 'arai')
r.lpush('league3-assist', 'None', 'shimabukuro', 'jinkawa','arai')

r.hmset('league4-info', {'label':'league4', 'date':'2018-05-19', 'opponent':'JAL FC', 'myscore':0, 'opponentscore':3, 'type':'official'})

r.hmset('league5-info', {'label':'league5', 'date':'2018-07-01', 'opponent':'DESEO東京', 'myscore':4, 'opponentscore':2, 'type':'official'})
r.lpush('league5-goal', 'arai', 'jinkawa', 'jinkawa', 'jinkawa')
r.lpush('league5-assist', 'None', 'arai', 'arai','katayama')

r.hmset('training1-info', {'label':'training1', 'date':'2018-01-08', 'opponent':'FC Bandelie', 'myscore':1, 'opponentscore':1, type:'training'})
r.lpush('training1-goal', 'kagata')
r.lpush('training1-assist', 'takada')

r.hmset('training2-info', {'label':'training2', 'date':'2018-01-21', 'opponent':'さいたま市役所', 'myscore':2, 'opponentscore':8, type:'training'})
r.lpush('training2-goal', 'hashimoto', 'ohno')
r.lpush('training2-assist', 'shimabukuro', 'tabuchi')

r.hmset('training3-info', {'label':'training3', 'date':'2018-01-27', 'opponent':'コンテナシティFC', 'myscore':2, 'opponentscore':4, type:'training'})
r.lpush('training3-goal', 'katayama', 'katayama')
r.lpush('training3-assist', 'fujikura', 'matsuda')


### メンバーの得点数とアシスト数を初期化
def main():

    ### 初期化
    initialize()

    ### 得点とアシストを記録
    set_result('league')
    set_result('training')

    ### 得点とアシストの表示
    output_result('league')

    ### 結果のプロット
    goal=np.array([])
    index=np.array([])
    type='league'
    i=0
    for member in memberlist:
        thisgoal=int(r.hget(member,'%s-goalnum'%type).decode('utf-8'))
        goal=np.append(goal,thisgoal)
        index=np.append(index,i)
        i+=1
    plt.figure(figsize=(25,10))
    plt.bar(index, goal, tick_label=memberlist, align="center")
    plt.xticks(rotation=300)
    plt.title('%s-goal'%type)
    plt.savefig('figure.png')

if __name__ == '__main__':
    main()

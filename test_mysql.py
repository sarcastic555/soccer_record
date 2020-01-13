import mysql.connector
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import math
import sys

sys.path.append('data/')
from namelist import name_list
from gameresultlist import result_list
from scorerlist import scorer_list
from participantlist import participant_list

### 個人成績用のtableを作成
def set_personal_table():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()    
    cur.execute('USE db')
    conn.commit()

    cur.execute("""DROP TABLE IF EXISTS test;""")
    cur.execute("""CREATE TABLE test(
 id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(20),
 number INT,
 goalnum_league INT,
 goalnum_training INT,
 goalnum_cup INT,
 assistnum_league INT,
 assistnum_training INT,
 assistnum_cup INT,
 participant_total DOUBLE,
 participant_training DOUBLE,
 participant_official DOUBLE,
 goalratio_total DOUBLE,
 goalratio_training DOUBLE,
 goalratio_official DOUBLE,
 assistratio_total DOUBLE,
 assistratio_training DOUBLE,
 assistratio_official DOUBLE);""")
    insert_name = "INSERT INTO test (name,number) VALUES (%s,%s);" 

    for name in name_list:
        cur.execute(insert_name, [name[0],name[1]])
    conn.commit()
    cur.close()
    conn.close()
    

### 試合情報を記録するtableの作成
def set_game_info():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    cur.execute("""DROP TABLE IF EXISTS result;""")
    cur.execute("""CREATE TABLE result(
 id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 date VARCHAR(20),
 type VARCHAR(20),
 setsu INT NOT NULL,
 opponent VARCHAR(30),
 mygoal INT,
 opponentgoal INT);""")
    
    insert_result = "INSERT INTO result (date, type, setsu, opponent, mygoal, opponentgoal) VALUES (%s,%s,%s,%s,%s,%s);" 
    for result in result_list:
        cur.execute(insert_result, result)
    conn.commit()
    cur.close()
    conn.close()

### 参加状況を記録するtableの作成
def set_participant_info():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    cur.execute("""DROP TABLE IF EXISTS participant;""")
    cur.execute("""CREATE TABLE participant(
 type VARCHAR(20),
 setsu INT NOT NULL,
 name VARCHAR(20));""")
    
    insert_participant = "INSERT INTO participant (type, setsu, name) VALUES (%s,%s,%s);" 
    for participant in participant_list:
        cur.execute(insert_participant, participant)
    conn.commit()
    cur.close()
    conn.close()

### 得点者、アシスト者の名前を記録するtableの作成
def set_goal_assit_name():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    cur.execute("""DROP TABLE IF EXISTS score;""")
    cur.execute("""CREATE TABLE score(
 id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 type VARCHAR(20),
 setsu INT,
 goaler VARCHAR(20),
 assister VARCHAR(20));""")

    insert_scorer = "INSERT INTO score (type, setsu, goaler, assister) VALUES (%s,%s,%s,%s);" 
    for scorer in scorer_list:
        cur.execute(insert_scorer, scorer)
    conn.commit()
    cur.close()
    conn.close()

### 得点、アシスト数の結果を個人成績tableに保存
def get_goal_assist_ranking():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()
    for goalassist in ['goal','assist']:
        for type in ['league','training','cup']:
            for name in name_list:
            #print(name)
                selection="""SELECT COUNT(*) FROM score WHERE %ser='%s' AND type='%s';"""%(goalassist,name[0],type)
                cur.execute(selection)
                goalnum=int(cur.fetchall()[0][0])
            #print(goalnum)
                addgoalnum="""UPDATE test SET %snum_%s=%d WHERE name='%s';"""%(goalassist,type,goalnum,name[0])
                cur.execute(addgoalnum)
    conn.commit()

### 参加状況の結果を個人成績tableに保存
def get_participant_ranking():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()
    ### 練習試合と公式戦の参加率の計算
    counttext="""SELECT COUNT(DISTINCT setsu) FROM participant where type='training'"""
    cur.execute(counttext)
    training_total_gamenum=int(cur.fetchall()[0][0])
    print(training_total_gamenum)
    counttext="""SELECT COUNT(DISTINCT setsu, type) FROM participant where type='league' OR type='cup'"""
    cur.execute(counttext)
    official_total_gamenum=int(cur.fetchall()[0][0])
    print(official_total_gamenum)
    for name in name_list:
        #print(name)
        ### 練習試合
        counttext="""SELECT COUNT(*) FROM participant WHERE name='%s' AND type='training';"""%(name[0])
        cur.execute(counttext)
        participate_num=float(cur.fetchall()[0][0])
        participate_rate=participate_num/training_total_gamenum*100.
        #print('training participant rate = %d/%d=%lf'%(participate_num,training_total_gamenum,participate_rate))
        addparticipaterate="""UPDATE test SET participant_training=%lf WHERE name='%s';"""%(participate_rate,name[0])
        cur.execute(addparticipaterate)
        ###公式戦
        counttext="""SELECT COUNT(*) FROM participant WHERE name='%s' AND (type='league' OR type='cup');"""%(name[0])
        cur.execute(counttext)
        participate_num=float(cur.fetchall()[0][0])
        participate_rate=participate_num/official_total_gamenum*100.
        #print('official participant rate = %d/%d=%lf'%(participate_num,official_total_gamenum,participate_rate))
        addparticipaterate="""UPDATE test SET participant_official=%lf WHERE name='%s';"""%(participate_rate,name[0])
        cur.execute(addparticipaterate)

    ## 全体の参加率を計算して詰める
    counttext="""SELECT COUNT(DISTINCT type, setsu) FROM participant"""
    cur.execute(counttext)
    total_gamenum=int(cur.fetchall()[0][0])
    for name in name_list:
        #print(name)
        counttext="""SELECT COUNT(*) FROM participant WHERE name='%s';"""%(name[0])
        cur.execute(counttext)
        participate_num=float(cur.fetchall()[0][0])
        participate_rate=participate_num/total_gamenum*100.
        #print(participate_num)
        #print(total_gamenum)
        addparticipaterate="""UPDATE test SET participant_total=%lf WHERE name='%s';"""%(participate_rate,name[0])
        cur.execute(addparticipaterate)
    
    conn.commit()

### 参加した試合あたりのゴール数、アシスト数の計算
def get_goal_assist_ranking_per_game():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()
    selection=['','AND (type=\'league\' OR type=\'cup\')', 'AND type=\'training\'']
    label=['total','official','training']
    for goalassist in ['goal','assist']:
        for i in range(len(selection)):
            for name in name_list:
                print(name)
            ### ゴール数、アシスト数を取得
                selecttext="""SELECT COUNT(*) FROM score WHERE %ser='%s' %s;"""%(goalassist,name[0],selection[i])
                cur.execute(selecttext)
                goalassistnum=int(cur.fetchall()[0][0])
                print('%snum=%d'%(goalassist,goalassistnum))
            ### 出席数を取得
                counttext="""SELECT COUNT(*) FROM participant WHERE name='%s' %s;"""%(name[0],selection[i])
                cur.execute(counttext)
                participate_num=float(cur.fetchall()[0][0])
                print('participate_num=%d'%participate_num)
                goalassist_ratio=0 if participate_num==0 else float(goalassistnum)/participate_num
                print('%s ratio=%lf'%(goalassist,goalassist_ratio))
                addresult="""UPDATE test SET %sratio_%s=%lf WHERE name='%s';"""%(goalassist,label[i],goalassist_ratio,name[0])
                cur.execute(addresult)
    conn.commit()


### 得点ランキングのプロットを作成
def create_goal_ranking():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    df=pd.read_sql_query("""SELECT name, goalnum_league+goalnum_training+goalnum_cup AS total, goalnum_training AS training, goalnum_league+goalnum_cup AS official FROM test;""",conn)
    df.index=df['name']
    df=df.sort_values('total',ascending=False)
    plt.figure(figsize=(30,5))
    df.plot.bar()
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.25)

    ylabel_max=math.ceil(df['total'].max()/5+1)*5
    plt.yticks( np.arange(0, ylabel_max, 5) )

    plt.xticks(rotation=90)
    plt.title('goal ranking')
    plt.savefig('goal_ranking.png')

### アシストランキングのプロットを作成
def create_assist_ranking():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    df=pd.read_sql_query("""SELECT name, assistnum_league+assistnum_training+assistnum_cup AS total, assistnum_training AS training, assistnum_league+assistnum_cup AS official FROM test;""",conn)
    df.index=df['name']
    df=df.sort_values('total',ascending=False)
    plt.figure(figsize=(30,5))
    df.plot.bar()

    ylabel_max=math.ceil(df['total'].max()/5+1)*5
    plt.yticks( np.arange(0, ylabel_max, 5) )
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.25)
    plt.xticks(rotation=90)
    plt.title('assist ranking')
    plt.savefig('assist_ranking.png')

### 得点とアシストの和のランキングのプロットを作成
def create_goal_puls_assist_ranking():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    df=pd.read_sql_query("""SELECT name, assistnum_league+assistnum_training+assistnum_cup+goalnum_league+goalnum_training+goalnum_cup AS "goal+assist", assistnum_league+assistnum_training+assistnum_cup AS assist, goalnum_league+goalnum_training+goalnum_cup AS goal FROM test;""",conn)
    df.index=df['name']
    df=df.sort_values('goal+assist',ascending=False)
    plt.figure(figsize=(30,5))
    df.plot.bar()

    ylabel_max=math.ceil(df['goal+assist'].max()/5+1)*5
    plt.yticks( np.arange(0, ylabel_max, 5) )
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.25)
    plt.xticks(rotation=90)
    plt.title('goal+assist ranking')
    plt.savefig('goalplusassit_ranking.png')

### 得点とアシストの相関プロットを作成
def create_goal_assist_scatter():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    df=pd.read_sql_query("""SELECT name, number, assistnum_league+assistnum_training+assistnum_cup AS assist, goalnum_league+goalnum_training+goalnum_cup AS goal FROM test;""",conn)
    fig=df.plot.scatter(x='assist', y='goal')
    for i in range(len(df)):
        goal=df.iloc[i]['goal']
        assist=df.iloc[i]['assist']
        number=df.iloc[i]['number']
        fig.annotate(str(number), xy=(assist,goal), size=15)
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.25)
    plt.xlabel('total assist number')
    plt.ylabel('total goal number')
    xlabel_max=math.ceil(df['assist'].max()/5+1)*5
    plt.xticks( np.arange(0, xlabel_max, 5) )
    ylabel_max=math.ceil(df['goal'].max()/5+1)*5
    plt.yticks( np.arange(0, ylabel_max, 5) )
    plt.title('goal & assist correlation')
    plt.xticks( np.arange(0, 20, 5) )
    plt.savefig('goal_assist_correlation.png')

### 参加率のプロットを作成
def create_participant_ranking():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    df=pd.read_sql_query("""SELECT name, participant_total AS average, participant_training AS training, participant_official AS official FROM test;""",conn)
    df.index=df['name']
    df=df.sort_values('average',ascending=False)
    plt.figure(figsize=(35,10))
    df.plot.bar()

    #ylabel_max=math.ceil(df[''].max()/5+1)*5
    #plt.yticks( np.arange(0, ylabel_max, 5) )
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.25)
    plt.xticks(rotation=90)
    plt.title('participant ranking')
    plt.savefig('participant_ranking.png')

### 試合数あたりの得点、アシストランキングのプロットを作成
def create_goal_assist_ranking_perday():
    conn = mysql.connector.connect(user='root',password='mysqlMYSQL@555',host='localhost')
    cur=conn.cursor()
    cur.execute('USE db')
    conn.commit()

    for goalassist in ['goal','assist']:
        df=pd.read_sql_query("""SELECT name, %sratio_total AS average, %sratio_training AS training, %sratio_official AS official FROM test;"""%(goalassist,goalassist,goalassist),conn)
        print(df)
        df.index=df['name']
        df=df.sort_values('average',ascending=False)
        plt.figure(figsize=(30,5))
        df.plot.bar()

        plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.25)
        plt.xticks(rotation=90)
        plt.ylabel('%s per game'%goalassist)
        plt.title('%s ranking per game'%goalassist)
        plt.savefig('%s_ranking_per_game.png'%goalassist)

if __name__ == '__main__':

    
    set_personal_table()
    set_game_info()
    set_participant_info()
    set_goal_assit_name()

    get_goal_assist_ranking()
    get_participant_ranking()
    get_goal_assist_ranking_per_game()

    create_goal_ranking()
    create_assist_ranking()
    create_goal_puls_assist_ranking()
    create_goal_assist_scatter()
    create_participant_ranking()
    create_goal_assist_ranking_perday()

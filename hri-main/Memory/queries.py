import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

from Memory.dbConnection import cursor, dbConnection

def getUser(username):

    # Eseguire una query
    query = "SELECT * FROM user WHERE username = %s"
    parametri = (username,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)

    # Ottenere i risultati
    result = cursor.fetchall()

    return result

def createUser(username):

    # Eseguire una query
    query = '''
    INSERT ignore INTO user 
        (username) 
    values 
        (%s);
    '''
    parametri = (username, )  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    dbConnection.commit()

    new_account = True
    if cursor.lastrowid == 0:
        new_account = False

    query = '''
    INSERT ignore INTO tris_instance 
        (idUser, level) 
    values 
        ((SELECT idUser FROM user where username = %s), 'BEGINNER');
    '''

    parametri = (username, )  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    dbConnection.commit()

    query = '''
    INSERT ignore INTO shoot_instance 
        (idUser) 
    values 
        ((SELECT idUser FROM user where username = %s));
    '''

    parametri = (username, )  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    dbConnection.commit()
    
    return {
            'success': True,
            'new_account': new_account
        }

def setWinner(username, winner):

    # Eseguire una query
    query = '''
    INSERT ignore INTO tris_match 
        (idUser, winner) 
    values 
        ((SELECT idUser FROM user WHERE username = %s), %s)'''
    parametri = (username, winner)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    dbConnection.commit()

    query = f"""
    UPDATE 
        tris_instance
    SET 
        {winner.lower()} = {winner.lower()} + 1 
    WHERE 
        idUser = (SELECT idUser FROM user WHERE username = %s);
    """
    
    parametri = (username, )  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    dbConnection.commit()
    
    return {
            'success': True
        }

def getMatches(username):

    # Eseguire una query
    query = '''
    SELECT 
        SUM(CASE WHEN winner = 'AI' THEN 1 ELSE 0 END) AS AI_wins,
        SUM(CASE WHEN winner = 'HUMAN' THEN 1 ELSE 0 END) AS human_wins,
        SUM(CASE WHEN winner = 'DRAW' THEN 1 ELSE 0 END) AS draw
    FROM 
        tris_match
    WHERE 
        idUser = (SELECT idUser from user where username = %s);
    '''
    parametri = (username,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    # Ottenere i risultati
    result = cursor.fetchall()

    return result

def getLevel(username):

    # Eseguire una query
    query = '''
    SELECT 
        level 
    FROM 
        tris_instance 
    WHERE 
        idUser = (SELECT idUser from user where username = %s)
    '''
    parametri = (username,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)

    # Ottenere i risultati
    result = cursor.fetchall()

    return result

def setLevel(username, level):

    
    query = '''
    INSERT INTO tris_instance
        (idUser, level) 
    values 
        ((SELECT idUser FROM user WHERE username = %s), %s)
    ON DUPLICATE KEY
    UPDATE
        level = %s
    '''
    # Eseguire una query
    
    parametri = (username, level, level,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    # Ottenere i risultati
    dbConnection.commit()

    # Controlla se è stata inserita una nuova riga o aggiornata una esistente
    if cursor.rowcount == 0:
        print("Nothing changed")
        return 'not_changed'
    if cursor.rowcount == 1:
        print("Inserita una nuova riga.")
        return 'created'
    elif cursor.rowcount == 2:
        print("Aggiornata una riga esistente.")
        return 'changed'

def getAngerLevel(username):
    # Eseguire una query
    query = '''
    SELECT 
        angerCounter 
    FROM 
        tris_instance 
    WHERE 
        idUser = (SELECT idUser from user where username = %s)
    '''
    parametri = (username,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)

    # Ottenere i risultati
    result = cursor.fetchall()

    return result
    

def setAngerCounter(username, newAngerCounter):
    query = '''
    UPDATE 
        tris_instance
    SET 
        angerCounter = %s
    WHERE
        idUser = (SELECT idUser FROM user WHERE username = %s)
    '''
    # Eseguire una query
    
    parametri = (newAngerCounter, username,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    # Ottenere i risultati
    dbConnection.commit()
    
    return

def deleteRecordForNewLevel(username, ratio):
    query = """
        call deleteRecordForNewLevel(%s, %s)
    """

    parametri = (username, ratio,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    # Ottenere i risultati
    dbConnection.commit()

    return

def createRecordForNewLevel(username, ratio):
    query = """
        call createRecordForNewLevel(%s, %s);
    """

    parametri = (username, ratio,)  # i parametri devono essere forniti in una tupla

    cursor.execute(query, parametri)
    # Ottenere i risultati
    dbConnection.commit()



if __name__ == "__main__":
    # user = getUser("buitr")
    # print(f"user: {user}")

    # createUser("buitr")
    # res = checkLevel('b')
    # res = setLevel('b', 'PRO')
    # res = getLevel('b')
    # res = getMatches('b')
    # print(res)

    # deleteRecordForNewLevel('b', 3)
    setWinner('b', 'AI')
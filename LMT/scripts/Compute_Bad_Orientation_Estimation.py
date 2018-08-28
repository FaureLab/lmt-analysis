'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from database.Animal import *
import matplotlib.pyplot as plt
from database.Event import *
from database.Measure import *
from database import BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,BuildEventOralOralContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, \
    BuildEventStop, BuildEventWaterPoint, \
    BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak,\
    BuildEventSideBySide, BuildEventSideBySideOpposite, BuildEventDetection,\
    BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP,\
    BuildEventOralSideSequence, CheckWrongAnimal,\
    CorrectDetectionIntegrity
    
    
from tkinter.filedialog import askopenfilename
from database.TaskLogger import TaskLogger
import sys
import traceback

max_dur = 3*oneDay


class FileProcessException(Exception):
    pass

def getScalarProduct( a, b ):

    return a.x * b.x + a.y * b.y;

def isSameSign( a, b ):
    if ( a >= 0 and b >= 0 ):
         return True;
    if ( a < 0 and b < 0 ):
        return True;
    return False;


def process( file ):

    print(file)
    
    chronoFullFile = Chronometer("File " + file )
    
    connection = sqlite3.connect( file )        
        
                        
    try:

        animalPool = None
        
        print("Caching load of animal detection...")
        animalPool = AnimalPool( )
        animalPool.loadAnimals( connection )
        animalPool.loadDetection( start = 0, end = max_dur )
        print("Caching load of animal detection done.")

        for animal in animalPool.getAnimalList():
            
            badOrientationTimeLine = EventTimeLine( None, "bad orientation" , animal.baseId , None , None , None , loadEvent=False )
            print ("Processing", animal )
            for t in range( 0, 10000 ):
                
                orientation = animal.getOrientationVector( t )
                speedVector = animal.getSpeedVector( t )
                speed = animal.getSpeed( t )

                if ( orientation != None and speedVector != None and speed != None ):
                    if ( speed > SPEED_THRESHOLD_HIGH ):
                        
                        scalar = getScalarProduct( orientation , speedVector )
                        
                        if ( scalar > 0 ):
                            badOrientationTimeLine.addPunctualEvent( t )
           
            badOrientationTimeLine.removeEventsBelowLength( 30 )
            badOrientationTimeLine.endRebuildEventTimeLine(connection)

            # faire un event de tout ca
            # faire un plot des erreur en histogramme binn de temps

        chronoFullFile.printTimeInS()
        
    except:
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error = ''.join('!! ' + line for line in lines)
        
        t = TaskLogger( connection )
        t.addLog( error )
        
        print( error, file=sys.stderr ) 
        
        raise FileProcessException()
        

if __name__ == '__main__':
    
    print("Code launched.")
     
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    chronoFullBatch = Chronometer("Full batch" )    
    
    for file in files:
        '''
        from multiprocessing.dummy import Pool as ThreadPool 
        pool = ThreadPool(4) 
        results = pool.map( process, files )
        pool.close()
        pool.join()
        '''
        try:
            process( file )
        except FileProcessException:
            print ( "STOP PROCESSING FILE " + file , file=sys.stderr  )
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")
        
        
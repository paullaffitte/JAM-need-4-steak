#!/usr/bin/env python3

import os
import sys

class Napi():
    def __init__(self):
        self.__rays = []
        self.__started = False
        self.__update = self.__defaultUpdate
        self.__response = None
        self.__lock = False
        self.__status = (1, "OK")
        self.__history = []

    def isStarted(self):
        """Return the current status of the Napi object (started or stopped)."""
        return self.__started

    @staticmethod
    def debug(data):
        """Display data to the error output."""
        print(data, file=sys.stderr)
    
    def getHistory(self):
        """Get an history of the user commands."""
        return self.__history
    
    def getStatus(self):
        """Get the current status of the API."""
        return self.__status

    def getRayAt(self, index):
        """Return the ray at the given index. If the index is out of range, the first item of the array is returned"""
        return self.__rays[index] if index >= 0 and index < len(self.__rays) else self.__rays[0]

    def getAverageRay(self):
        """Return the average length of the rays"""
        return sum(self.__rays) / len(self.__rays)

    def getRays(self):
        """Return an array of rays for the current turn"""        
        return self.__rays
    
    def getDirection(self):
        """ Return the length of the ray placed ahead of the car"""
        return (self.__rays[15] + self.__rays[16]) / 2
    
    def getMinRay(self):
        """Return the shortest ray in the array for the current turn"""
        value = min(self.__rays)
        return (self.__rays.index(value), value)
    
    def getMaxRay(self):
        """Return the longest ray in the array for the current turn"""        
        value = max(self.__rays)
        return (self.__rays.index(value), value)
    
    def getResponse(self):
        """Return the response stored for the current turn (COMMAND_AS_STRING, VALUE_AS_FLOAT)"""        
        return self.__response

    def setThrust(self, value, force = False, refresh = False):
        """Set the thrust for the car, the power given as value must be a float between -1 and 1"""        
        if self.__locked(force): return

        thrust_direction = "CAR_" + ("FORWARD" if value > 0 else "BACKWARDS")
        value = min(1, abs(value))
        self.__setResponse((thrust_direction, value))

        if refresh: self.__send()        

    def setDirection(self, value, force = False, refresh = False):
        """Set the wheels direction, the angle given as value must be a float between -1 (left) and 1 (right)."""
        if self.__locked(force): return

        if value < -1: value = -1
        elif value > 1: value = 1
        self.__setResponse(("WHEELS_DIR", value))

        if refresh: self.__send()
    
    def start(self, f = None):
        """Start the API"""
        self.__setResponse(("START_SIMULATION", 0))
        self.__send(True)
        self.__started = True
        if f is not None: self.__update = f
        while (self.__started):
            self.__getValues()
            self.__update()
            self.__send()
        self.stop()

    def stop(self):
        """Stop the API"""
        print("STOP_SIMULATION")
        self.__started = False

    def __getValues(self):
        self.__setResponse(("GET_INFO_LIDAR", 0))
        resp = self.__send(True).split(':')
        self.__status = (int(resp[0]), resp[1])
        if resp[1] == 'KO': return
        self.__rays = list(map(float, resp[3:35]))

    def __defaultUpdate(self):
        self.setThrust(1)
    
    def __setResponse(self, response):
        self.__response = response
        self.__lock = True        
    
    def __send(self, inline=False):
        self.__lock = False
        if self.__response is None: return
        cmd = self.__response[0] + ((":" + str(self.__response[1])) if not inline else "")
        self.__history.append(cmd)
        print(cmd)
        resp = input()
        self.__response = None
        return resp
    
    def __locked(self, force = False):
        if self.__lock and not force:
            Napi.debug("Failed to exec command, consider adding the 'force=True' parameter in you method call")
        return self.__lock and not force

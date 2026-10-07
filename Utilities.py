import random
import asyncio
import os
import sys
import json
from os import path
import subprocess as sbp
import typing as ty
from dataclasses import dataclass
from typing import(
	TypedDict,
	Any
) 
import termcolor as tc
import colour as colorist
import colorsys as colconv
from enum import Enum, IntEnum
import re
from pathlib import Path
from datetime import datetime as dt
import threading as tr
from time import sleep

Number = int|float
def Clamp(n:Number,lb:Number,ub:Number):
	if lb == ub: return lb
	elif lb > ub: lb,ub = ub, lb
	
	if n < lb: return lb
	elif n > ub: return ub
	return n

ThreadDict:dict[str,tr.Thread] = {}
def Thread(func:ty.Callable, name:str, Daemon:bool = False, *args, **kwargs):
	ThreadDict[name] = tr.Thread(
		target=func,
		daemon=Daemon,
		args=args,
		kwargs=kwargs
	)

def pthChain(stub, end):
	return path.join(stub, end)

def GetUUID(len:int = 5):
	n = str(random.randint(
		0,(10 ** len) - 1
	))
	f = "{" + f":>0{len}" + "}"
	
	return f.format(n)

sT = ty.TypeVar("sT",bound=type)
T = ty.TypeVar("T",covariant=True)

class protoSingleton(ty.Protocol[T]):
	def __call__(self, *args, **kwargs) -> T: ...

	@classmethod
	def Destroy(cls) -> None: ...

def singleton(_cls:type[T]) -> protoSingleton[T]|type[T]:
	class sub(_cls):
		__created:bool = False
		__inst:T|None = None

		def __new__(cls, *args, **kwargs) -> T:
			if not cls.__created:
				cls.__created = True
				cls.__inst = _cls(*args,**kwargs)
			assert cls.__inst != None
			return cls.__inst

		@classmethod
		def Destroy(cls):
			cls.__inst = None
			cls.__created = False
			
	return sub

FOLDER_REGEX = r"^(?:[^?\\/\*\"\:|<>]*)*$"

PATH_REGEX = r"^(?:[^?\\\*\"\:|<>]*)*$"

if __name__ == "__main__":
	print(GetUUID())
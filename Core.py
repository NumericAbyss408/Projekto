from pathlib import Path
import showinfm.showinfm as fm
from weakref import WeakValueDictionary

import Utilities as UTIL

#import Gui as UI

#region Projekts
class Projekt:
	#region CLASS:
	PROJEKT_DTL_FILE = "_projesh.dtl"
	class JSON(UTIL.TypedDict): # Format of _projesh.dtl
		Name:str
		Identifier:str
		Description:str
		Tags:list[str]
		Tasks:list[Task.JSON]

	_instances:WeakValueDictionary[str,Projekt] = WeakValueDictionary()

	@classmethod
	def DefinedAt(cls,dir:Path):
		Check1 = dir.is_dir() and dir.is_absolute() and dir.exists()
		if not Check1: return False

		dtlPath = dir / Projekt.PROJEKT_DTL_FILE
		Check2 :bool = dtlPath.exists() #(Projekt.PROJEKT_DTL_FILE in UTIL.os.listdir(dir))
		if not Check2: return False

		with dtlPath.open() as projesh:
			Check3 :Projekt.JSON = UTIL.json.loads(projesh.read())
			try:
				for k in Projekt.JSON.__annotations__:
					assert Check3.get(k,False) != False
			except AssertionError: return False

		return True

	@classmethod
	def Load(cls, dir:Path):
		with open(f"{dir}/{Projekt.PROJEKT_DTL_FILE}") as projesh:
			LoadedJson: Projekt.JSON = UTIL.json.loads(projesh.read())
			if Projekt._instances.get(LoadedJson["Identifier"]) != None:
				return Projekt._instances[LoadedJson["Identifier"]]
			return cls(
				dir,
				LoadedJson["Name"],
				LoadedJson["Identifier"],
				LoadedJson["Description"],
				[
					Tag.Instances[item]
					for item in LoadedJson["Tags"]
					if Tag.Instances.get(item,False) != False
				],
				[
					Task(
						item["Name"],
						item["Description"],
						item["Deadline"],
						item["Complete"]
					)
					for item in LoadedJson["Tasks"]
				]
			)

	@classmethod
	def New(
		cls,
		ParDir:Path,
		Name:str,
		Description:str,
		TagList: list[Tag] = []
	):
		projektPath = ParDir / Name
		projektPath.mkdir(exist_ok=True)
		id = UTIL.GetUUID(7)
		with (projektPath / Projekt.PROJEKT_DTL_FILE).open("w") as projesh:
			payload: Projekt.JSON = {
				"Name": Name,
				"Identifier":id ,
				"Description": Description,
				"Tags":[tag.identifier for tag in TagList],
				"Tasks": []
			}
			projesh.write(UTIL.json.dumps(payload))
		inst = cls(projektPath, Name, id, Description, TagList, [])
		Projekt._instances[id] = inst
		return inst

	@classmethod
	def CollectFromDir(cls, dir:str, recursive:bool = True):
		result :list[Projekt] = []

		def Inner(dir:str):
			DirObj = Path(dir)

			ValidityCheck = DirObj.is_absolute() and DirObj.exists() and DirObj.is_dir()
			if not ValidityCheck: return

			for pth in DirObj.iterdir():
				if not pth.is_dir(): continue
				if Projekt.DefinedAt(pth):
					result.append(Projekt.Load(pth))
					
				if recursive: Inner((str(pth)))

		Inner(dir)
		
		return result

	def __repr__(self) -> str:
		return self._name
	
	#endregion

	#region INSTANCE
	def __init__(
		self,
		FileDir:Path,
		Name:str,
		Identifier:str,
		Description:str,
		TagList:list["Tag"],
		TaskList:list["Task"]
	):
		self._folder = FileDir
		self._name = Name
		self._id = Identifier
		self._desc = Description
		self._Tags =  TagList
		self._Tasks = TaskList

	def GetName(self): return self._name
	def SetName(self, nominal:str): self._name = nominal

	def GetDescription(self): return self._desc
	def SetDescription(self, nDesc:str): self._desc = nDesc

	def GetTags(self): return self._Tags
	def SetTags(self,tags:list[Tag]) -> None: self._Tags = tags

	def GetTasks(self): return self._Tasks

	def GetContent(self) -> list[str]:
		FolderContent = [
			c.resolve().name
			for c in self._folder.iterdir()
			if not (c.is_dir() and Projekt.DefinedAt(c.resolve()))
			and c.name != Projekt.PROJEKT_DTL_FILE
		]

		return FolderContent

	def GetFolder(self): return self._folder

	def Save(self):
		with (self._folder / self.PROJEKT_DTL_FILE).open("w") as projesh:
			payload:Projekt.JSON = {
				"Name": self._name,
				"Identifier": self._id,
				"Description": self._desc,
				"Tags": [
					tag.identifier
					for tag in self._Tags
				],
				"Tasks": [
					{
						"Name": task.Name,
						"Description": task.Description,
						"Deadline": task.Deadline,
						"Complete": task.Complete
					}
					for task in self._Tasks
				]
			}
			projesh.write(UTIL.json.dumps(payload, indent="\t"))

	def OpenInExplorer(self):
		fm.show_in_file_manager(
			str(self._folder)
		)

	#endregion

#endregion

#region Tags
class Tag:
	#region CLASS
	TAG_KTO_FILE = "tagfile.kto"
	class JSON(UTIL.TypedDict):
		name:str
		color:str
	
	Instances: dict[str,"Tag"] = {}

	@classmethod
	def LoadTags(cls):
		with (Path(Settings().GetSuperDir()) / Tag.TAG_KTO_FILE).open() as tagfile:
			ktoStruct: dict[str,Tag.JSON] = UTIL.json.loads(tagfile.read())
			Tag.Instances = {
				id: Tag(
					id,
					ktoStruct[id]["name"],
					ktoStruct[id]["color"]
				)
				for id in ktoStruct
			}

	@classmethod
	def New(cls, name:str, color:str):
		return cls(UTIL.GetUUID(), name, color)

	@classmethod
	def Save(cls):
		with (Path(Settings().GetSuperDir())/Tag.TAG_KTO_FILE).open("w") as tagfile:
			tagfile.write(UTIL.json.dumps({
				tagid: {
					"name": Tag.Instances[tagid].name,
					"color": Tag.Instances[tagid].color
				}
				for tagid in Tag.Instances
			}, indent="\t"))


	#endregion

	#region INSTANCE
	def __init__(self, identifier:str, name:str, color:str) -> None:
		self.identifier = identifier
		self.name = name
		self.color = color
		Tag.Instances[identifier] = self

	def __repr__(self) -> str:
		pCol = UTIL.colorist.hex2rgb(self.color)
		pCol = (
			int(pCol[0] * 255),
			int(pCol[1] * 255),
			int(pCol[2] * 255)
		)
		return UTIL.tc.colored(
			text=f"{self.name} ({self.identifier})",
			color=pCol
		) 

	def __str__(self) -> str:
		return self.__repr__().replace(f"({self.identifier})","")

	
	#endregion
#endregion

#region Tasks
class Task:
	#region CLASS
	class JSON(UTIL.TypedDict):
		Name:str
		Description:str
		Deadline:str
		Complete:bool
	#endregion

	#region INSTANCE
	def __init__(
		self,
		Name:str,
		Desc:str,
		Dead:str,
		State:bool
	) -> None:
		self.Name = Name
		self.Description = Desc
		self.Deadline = Dead
		self.Complete = State
	#endregion
#endregion

#region Config
@UTIL.singleton
class Settings:
	pass
	#region CLASS
	STNG_FILE = "settings.kto"

	class SettingsJSON(UTIL.TypedDict):
		SuperDirectory: str
		HiltTheme: Settings.HiltThemeJSON
		
	class HiltThemeJSON(UTIL.TypedDict):
		FlatColor:str
		EdgeColor:str
		GuardColor:str
		HiltColor:str
		OrnationMode:Settings.OrnationModeENUM

	class OrnationModeENUM(UTIL.IntEnum):
		BOUND = 1
		UNBOUND = 2
		CONTOUR = 3

	#endregion

	#region INSTANCE
	def __init__(self) -> None:
		with open(Settings.STNG_FILE) as settingsfile:
			LoadedJSON: Settings.SettingsJSON = UTIL.json.loads(settingsfile.read())
			self._MainDir = Path(LoadedJSON["SuperDirectory"])
			self._Theme = LoadedJSON["HiltTheme"]

	def GetSuperDir(self):
		return self._MainDir
	
	def SetSuperDir(self,dir:str):
		dirObj = Path(dir)
		if not (dirObj.is_absolute() and dirObj.is_dir() and dirObj.exists()):
			return
		
		self._MainDir = dirObj

	def GetTheme(self):
		return self._Theme

	def Save(self):
		with open(Settings.STNG_FILE, "w") as settingsfile:
			state: Settings.SettingsJSON = {
				"SuperDirectory": str(self._MainDir),
				"HiltTheme": self._Theme
			}
			settingsfile.write(UTIL.json.dumps(state,indent="\t"))
		
	#endregion
#endregion

#region Main

def Search(
	dir:str,
	nameRX:str,
	filterTagList:list[Tag]
):
	#gets projects in the directory, if the directory exists.
	#will usually be true, only possibly false if superdir is invalid
	InitialList = Projekt.CollectFromDir(dir)

	#filters projets by name. empty strings match all projects.
	nameFilteredList = [
		p
		for p in InitialList
		if UTIL.re.match(
			f".*{nameRX}.*",
			p._name, 
			UTIL.re.IGNORECASE
		) != None
	]

	#filters projekts by tag. 
	#all tags in the filterlist must be present in the projekt 
	#for the projekt to be selected
	TagFilteredList = [
		p
		for p in nameFilteredList
		if not (False in [(tag in p.GetTags()) for tag in filterTagList])
	]

	return TagFilteredList

# returns a parent projekt path or the superdirectory
def GetParentAugmentedDirectory(cwd:Path):
	pth = Path(cwd).parent
	while (not Projekt.DefinedAt(pth)):
		if str(pth) == str(Settings().GetSuperDir()):
			break
		pth = pth.parent

	return pth

def GetProjektChain(cwd:Path):
	pList = []
	pth = cwd
	while (str(pth) != str(Settings().GetSuperDir())):
		if Projekt.DefinedAt(pth): pList.append(pth)
		pth = pth.parent
	pList.append(Settings().GetSuperDir())
	pList.reverse()
	return pList

def Setup():
	try:
		with open(Settings.STNG_FILE, "x") as stngfile:
			defaultJSON: Settings.SettingsJSON = {
				"SuperDirectory": str(Path.home()),
				"HiltTheme": {
					"FlatColor": "#232323",
					"EdgeColor": "#AF1212",
					"GuardColor": "#AFAD12",
					"HiltColor": "#1212AF",
					"OrnationMode": Settings.OrnationModeENUM.BOUND
				}
			}
			stngfile.write(UTIL.json.dumps(defaultJSON))
	except FileExistsError: pass
	Settings()
	try: 
		with (Settings().GetSuperDir() / Tag.TAG_KTO_FILE).open("x") as tagfile:
			tagfile.write("{}")
	except FileExistsError: pass
	Tag.LoadTags()

def Terminate():
	print("Terminating")
	for p in Projekt._instances:
		Projekt._instances[p].Save()
	print("Saved remaining Projekts")
	Tag.Save()
	print("Saved Tags")
	Settings().Save()
	print("Saved Settings")

if __name__ == "__main__": pass

#endregion
import flet as ft
from Core import (
	Projekt as p,
	Tag as t, 
	Task as tk,
	Settings as cf
)

import Core
import Theme as th


import Utilities as UTIL


#region MISC
class HexHSVColorPicker(ft.Container):
	HANDLR = UTIL.ty.Callable[[ft.Event["HexHSVColorPicker"]],UTIL.Any]|None
	def __init__(
		self, 
		h:float=0,s:float=1,v:float=1,
		on_color_changed: HANDLR = None
	):
		###

		self.hsv = [h,s,v]

		self.on_color_changed = on_color_changed

		self._ColorDisplay = ft.Container(
			aspect_ratio=3,
			expand=True
		)

		self.HueSlider = ft.Slider(
			value=h,
			min=0,
			max=1,
			thumb_color= ft.Colors.RED,
			padding=0,
			active_color=ft.Colors.BLACK,
			inactive_color=ft.Colors.BLACK
		)
		self.HueContainer = ft.Container(
			expand_loose=True,
			content=self.HueSlider,
			gradient= ft.LinearGradient(
				colors=[
					ft.Colors.RED,
					ft.Colors.GREEN,
					ft.Colors.BLUE,
					ft.Colors.RED
				]
			)
		)

		self.SaturationSlider = ft.Slider(
			value=s,
			min=0,
			max=1,
			thumb_color= ft.Colors.RED,
			padding=0,
			active_color=ft.Colors.BLACK,
			inactive_color=ft.Colors.BLACK
		)
		self.SaturationContainer = ft.Container(
			expand_loose=True,
			content=self.SaturationSlider,
			gradient= ft.LinearGradient(
				colors=[
					ft.Colors.WHITE,
					ft.Colors.WHITE,
				]
			)
		)

		self.ValueSlider = ft.Slider(
			value=v,
			min=0,
			max=1,
			thumb_color= ft.Colors.RED,
			padding=0,
			active_color=ft.Colors.BLACK,
			inactive_color=ft.Colors.BLACK
		)
		self.ValueContainer = ft.Container(
			expand_loose=True,
			content=self.ValueSlider,
			gradient= ft.LinearGradient(
				colors=[
					ft.Colors.BLACK,
					ft.Colors.RED,
				]
			)
		)
		

		###
		self._mainColumn = ft.Column(
			controls=[
				self._ColorDisplay,
				self.HueContainer,
				self.SaturationContainer,
				self.ValueContainer
			],
			expand=True,
			horizontal_alignment= ft.CrossAxisAlignment.CENTER
		)

		###
		super().__init__(
			padding=10,
			content= self._mainColumn,
			expand=True
		)
		self.CurrentColor = self.UpdateColor()

	def did_mount(self):
		async def UpdateLoop():
			while True:
				self.UpdateColor()
				await UTIL.asyncio.sleep(1/20)

		#self.page.loop.create_task(UpdateLoop())
		return super().did_mount()

	def build(self):
		super().build()
		async def UpdateLoop():
			while True:
				self.UpdateColor()
				await UTIL.asyncio.sleep(1/20)
		
		self.page.loop.create_task(UpdateLoop())
		
	def UpdateColor(self):
		self.hsv:list[float] = [
			self.HueSlider.value,
			self.SaturationSlider.value,
			self.ValueSlider.value
		]
		def toHex(rgb:tuple[float,float,float]):
			hexlist = [
				"{:02X}".format(round(component * 255))
				for component in rgb
			]
			return f'#{hexlist[0]}{hexlist[1]}{hexlist[2]}'
		full = toHex(UTIL.colconv.hsv_to_rgb(*self.hsv))
		husat = toHex(UTIL.colconv.hsv_to_rgb(self.hsv[0],self.hsv[1],1))
		hue = toHex(UTIL.colconv.hsv_to_rgb(self.hsv[0],1,1))
		self._ColorDisplay.bgcolor = full

		self.HueSlider.thumb_color = hue

		self.SaturationSlider.thumb_color = husat
		self.SaturationContainer.gradient.colors[1] = hue

		self.ValueSlider.thumb_color = full
		self.ValueContainer.gradient.colors[1] = husat

		self.CurrentColor = full

		if self.on_color_changed != None:
			self.on_color_changed(ft.Event(name="",control=self,data=full))

		try: self.update()
		except RuntimeError: pass

	def SetWithHex(self, hexstring:str):
		tpl = UTIL.colconv.rgb_to_hsv(
			*UTIL.colorist.hex2rgb(hexstring)
		)
		self.HueSlider.value = tpl[0]
		self.SaturationSlider.value = tpl[1]
		self.ValueSlider.value = tpl[2]

#endregion

#region ProjektEditor

#region Overlays
@UTIL.singleton
class TagSelector(ft.Container):
	def __init__(self):
		###
		self.selected:list[TagView] = []
		
		self.TagColumn = ft.Column(
			expand= 5,
			controls= []
		)

		self.ButtonColumn = ft.Column(
			expand= 4,
			controls= []
		)
		###
		self.QuitButton = ft.Container(
			expand=1,
			aspect_ratio=2,
			bgcolor="#f33",
			align= ft.Alignment.TOP_RIGHT,
			content= ft.Icon(ft.Icons.CLOSE),
			on_click= lambda evt: self.Close()
		)
		self.level2Column = ft.Column(
			expand=True,
			controls= [
				self.TagColumn,
				self.ButtonColumn
			]
		)
		###
		self._intermediateContainer = ft.Container(
			expand=19,
			padding= ft.Padding(10,0,10,0),
			content=self.level2Column
		)

		###
		self.level1Column = ft.Column(
			expand=True,
			controls=[
				self.QuitButton,
				self._intermediateContainer
			]
		)

		###
		super().__init__(
			expand=True,
			bgcolor= ft.Colors.GREY_900,
			content= self.level1Column,
			visible= False,
			left=15, right=15, top=15, bottom=15
		)
		th.MockOrnationMode(
			lambda:th.ApplyContainerTheme(
				self,
					th.ThemeColors["HiltColor"]
			),
			cf.OrnationModeENUM.CONTOUR
		)
		self.bgcolor = th.Dim(th.ThemedBG(), 80)

	def AddTagToSelection(self, inst:TagView):
		self.selected.append(inst)

	def RemoveTagFromSelection(self, inst:TagView):
		self.selected.remove(inst)

	def Open(
			self,
			Callbacks: list[tuple[str,str,UTIL.ty.Callable[[list[t]],None]]]
		):
		self.selected.clear()
		self.TagColumn.controls = [
			TagView(
				t.Instances[inst],
				TagView.Form.NORMAL,
				True,
				False,
				False,
				OnSelectCallback= lambda evt: self.AddTagToSelection(evt.control),
				OnDeselectCallback= lambda evt: self.RemoveTagFromSelection(evt.control)
				
			)
			for inst in t.Instances
		]

		bArr = []
		for tpl in Callbacks:
			b = ft.Button(
				content=tpl[0],
				on_click=lambda evt: tpl[2]([
					view.GetTag() for view in self.selected
				]),
				align=ft.Alignment.CENTER
			)
			th.ApplyButtonTheme(b,tpl[1])
			bArr.append(b)
		self.ButtonColumn.controls = bArr
		self.visible = True

	def Close(self):
		self.visible = False

@UTIL.singleton
class ProjektCreator(ft.Container):
	def __init__(self):
		###
		self.TitleText = ft.TextField(
			value="",
			label="Projekt Name",
			expand=True,
			input_filter= ft.InputFilter(
				allow=True,
				regex_string= UTIL.FOLDER_REGEX
			),
			border= ft.NoInputBorder()
		)

		self.DescriptionText = ft.TextField(
			value="",
			label="Projekt Description",
			expand=True,
			border= ft.NoInputBorder()
		)
		###
		self._titleTextContainer = ft.Container(
			expand=2,
			bgcolor=ft.Colors.GREY_700,
			content= self.TitleText,
			padding= 10
		)

		self._DescriptionTextContainer = ft.Container(
			expand=5,
			bgcolor=ft.Colors.GREY_700,
			content= self.DescriptionText,
			padding= 10
		)
		self.TagList = ft.ListView(
			expand=3,
		)
		self.SelectTagsButton = ft.Button(
			expand=1,
			content= "Add Tags",
			icon= ft.Icons.TAG,
			on_click= lambda evt: self.PromptTagSelect(),
			align= ft.Alignment.CENTER
		)
		th.BTA_Accent(self.SelectTagsButton)

		self.CreateButton = ft.Button(
			expand=1,
			content= "Create",
			icon= ft.Icons.ADD,
			on_click= lambda evt: self.Create(),
			align= ft.Alignment.CENTER
		)
		th.BTA_Contrast(self.CreateButton)

		self.QuitButton = ft.Container(
			expand=1,
			aspect_ratio=2,
			bgcolor="#f33",
			align= ft.Alignment.TOP_RIGHT,
			content= ft.Icon(ft.Icons.CLOSE),
			on_click= lambda evt: self.Close()
		)

		###
		self._level1Column = ft.Column(
			expand=True,
			controls=[
				self.QuitButton,
				self._titleTextContainer,
				self._DescriptionTextContainer,
				self.TagList,
				self.SelectTagsButton,
				self.CreateButton
			]
		)

		###
		super().__init__(
			expand=True,
			bgcolor= ft.Colors.GREY_900,
			content= self._level1Column,
			visible= False,
			left=15, right=15, top=15, bottom=15,
			padding= 20
		)
		th.MockOrnationMode(
			lambda:th.ApplyContainerTheme(
				self,
					th.ThemeColors["HiltColor"]
			),
			cf.OrnationModeENUM.CONTOUR
		)
		self.bgcolor = th.Dim(th.ThemedBG(), 80)

	def Open(self):
		self.TitleText.value = ""
		self.DescriptionText.value = ""
		self.TagList.controls = []
		self.visible = True

	def Close(self):
		self.visible = False

	def PromptTagSelect(self):
		TagSelector().Open([
			("Add to Projekt", "#a0f",lambda sel: self.AddSelectedTags(sel))
		])

	def AddSelectedTags(self, selected:list[t]):
		TagSelector().Close()
		self.TagList.controls = [
			TagView(
				tag,
				TagView.Form.NORMAL,
				False,
				True,
				False,
				OnRemoveCallback= lambda evt:
					self.TagList.controls.remove(evt.control)
			)
			for tag in selected
			if not tag in [view.GetTag() for view in self.TagList.controls]
		]

	#create a projekt within the current working directory
	def Create(self):
		if (self.TitleText.value == "" or self.DescriptionText.value == ""):
			return #no text

		newProjekt = p.New(
			NavigationBar().GetCurrentDir(),
			self.TitleText.value,
			self.DescriptionText.value,
			[view.GetTag() for view in self.TagList.controls]
		)

		NavigationBar().ScopeInto(
			newProjekt.GetName(),
			newProjekt.GetFolder()
		)

		self.Close()

#endregion

#region Views
class TagView(ft.Container):
	class Form(UTIL.Enum):
		MINI = 1
		NORMAL = 2

	BindableType = UTIL.ty.Callable[[ft.Event],None]
	
	def __init__(
		self,
		tag:t,
		TagForm:TagView.Form,
		selectable:bool,
		removable:bool,
		editable:bool,
		OnSelectCallback: TagView.BindableType|None = None,
		OnDeselectCallback: TagView.BindableType|None = None,
		OnRemoveCallback: TagView.BindableType|None = None,
		OnEditCallback: TagView.BindableType|None = None
	):
		self._tag = tag
		
		###
		self.LGem = ft.Container(aspect_ratio=1.5,expand=True)
		self.RGem = ft.Container(aspect_ratio=0.25,expand=True)
		self.NameLabel = ft.Text(
			tag.name,
			align= ft.Alignment.CENTER,
			text_align= ft.TextAlign.CENTER
		)

		bd = ft.BorderSide(
			width=0.5, color=ft.Colors.BLACK
		)
		self.EditButton = ft.Container(
			aspect_ratio= 1,
			content= ft.Icon(ft.Icons.EDIT),
			border= ft.Border(
				bd,bd,bd,bd
			),
			visible= editable,
			on_click= lambda evt: OnEditCallback(ft.Event(name="remove",control=self))
		)
		th.IC_AddInk(self.EditButton,th.Neu(self._tag.color))
		self.RemoveButton = ft.Container(
			aspect_ratio= 1,
			content= ft.Icon(ft.Icons.REMOVE),
			border= ft.Border(
				bd,bd,bd,bd
			),
			visible= removable,
			on_click= lambda evt: OnRemoveCallback(ft.Event(name="remove",control=self))
		)
		th.IC_AddInk(self.RemoveButton,th.Neu(self._tag.color))

		###
		self.ContentArray: list[ft.Control] = []
		self.ContentRow = ft.Row(
			controls=self.ContentArray,
			animate_scale= ft.Animation(250,ft.AnimationCurve.LINEAR_TO_EASE_OUT),
			on_animation_end= self.OnAnimationEnd
		)
		###
		self.level1Row = ft.Row(
			align= ft.Alignment.CENTER,
			controls=[
				self.ContentRow
			]
		)
		###
		self.Selectable = selectable
		self.Selected = False
		self.SelCallback = OnSelectCallback
		self.DeselCallback = OnDeselectCallback
		self.SelectionBd = ft.Border.all(
			3,
			color=th.Tint(th.ThemeColors["HiltColor"],75)
		)

		super().__init__(
			content= self.level1Row,
			bgcolor= th.taj(tag.color),
			on_click= self.AttemptSelection
		)

		match TagForm:
			case TagView.Form.NORMAL:
				self.ContentArray = [
					self.NameLabel,
					self.EditButton,
					self.RemoveButton
				]
				self.ContentRow.expand = True
				self.NameLabel.expand = True
				self.on_hover = None
				self.expand_loose = True
				self.aspect_ratio = 10
				self.level1Row.expand = True
				self.Expand()

			case TagView.Form.MINI:
				self.ContentRow.expand_loose = True
				self.LGem.bgcolor = self._tag.color
				ft.Text()
				self.level1Row.controls = [
					self.LGem,
					self.ContentRow
				]
				self.ContentArray = [
					self.NameLabel,
					self.RGem,
					self.EditButton,
					self.RemoveButton
				]
				
				self.expand_loose = True
				self.level1Row.expand_loose = True
				self.on_hover = self.OnHover
				self.OnContractEnd()
		self.ContentRow.controls = self.ContentArray
		
	def OnHover(self, evt:ft.Event[ft.Container]):
		match evt.data:
			case True: self.Expand()
			case False: self.Contract()

	def OnAnimationEnd(self, evt:ft.Event[ft.LayoutControl]):
		match evt.data:
			case "scale": 
				if self.ContentRow.scale.scale == 0: self.OnContractEnd()


	def Expand(self):
		self.ContentRow.width = None
		self.ContentRow.scale = ft.Scale(1,alignment=ft.Alignment.CENTER_LEFT)

	def Contract(self):
		self.ContentRow.scale = ft.Scale(0,alignment=ft.Alignment.CENTER_LEFT)

	def OnContractEnd(self):
		self.ContentRow.width = 0

	def AttemptSelection(self, evt:ft.Event[ft.Container]):
		if not self.Selectable: return
		match self.Selected:
			case False:
				self.border = self.SelectionBd
				self.Selected = True
				if self.SelCallback != None: self.SelCallback(evt)
			case True:
				self.border = None
				self.Selected = False
				if self.DeselCallback != None: self.DeselCallback(evt)

	def Select(self, toggle:bool):
		self.AttemptSelection(ft.Event(
			name="Select",
			control=self,
			data=toggle
		))
		
	def GetTag(self): return self._tag

class ProjektSimpleView(ft.Container):
	def __init__(self,projekt:p):
		self._projekt = projekt

		###
		self._TitleLabel = ft.Text(
			expand=True,
			align=ft.Alignment.CENTER_LEFT,
			value= self._projekt.GetName(),
		)

		self._TagRow = ft.ListView(
			spacing=0,
			horizontal=True,
			expand=True,
			controls= [
				TagView(
					tag,
					TagView.Form.MINI,
					False,
					False,
					False
				)
				for tag in self._projekt.GetTags()
			]
		)

		###
		self._TitleContainer = ft.Container(
			bgcolor="#00BD7E",
			expand=True,
			content=self._TitleLabel,
			padding=ft.Padding(10,0,0,0)
		)
		th.CTA_Contrast(self._TitleContainer)

		self._TagContainer = ft.Container(
			expand=True,
			content=self._TagRow,
			border_radius=5
		)

		###
		self._level1Column = ft.Column(
			expand=7,
			controls=[
				self._TitleContainer,
				self._TagContainer
			]
		)

		self._openButton = ft.Container(
			content= ft.Icon(ft.Icons.ARROW_RIGHT),
			expand=1,
			aspect_ratio=1,
			on_click= lambda evt: NavigationBar().NavInto(
				self._projekt.GetFolder()
			)
		)
		th.IC_AddInk(self._openButton)

		###
		self._level1Row = ft.Row(
			expand=True,
			controls= [
				self._level1Column,
				self._openButton
			]
		)

		###
		super().__init__(
			aspect_ratio=5,
			expand=True,
			content=self._level1Row,
			padding= ft.Padding(20,5,20,5)
		)
		th.MockOrnationMode(
			lambda: th.CTA_Accent(self),
			cf.OrnationModeENUM.CONTOUR
		)

@UTIL.singleton
class ProjektFullView(ft.Container):

	class ContentUnit(ft.Container):
		def __init__(self,content:str):
			self._content = content
			###
			self._text = ft.Text(
				value= content,
				align= ft.Alignment.CENTER_LEFT
			)
			self.ProjektConversionButton = ft.Container(
				aspect_ratio=1,
				content= ft.Icon(ft.Icons.FOLDER_OPEN),
				expand= True,
				align= ft.Alignment.CENTER_RIGHT,
				on_click= lambda evt: self.mkProjekt(),
				visible=False
			)
			th.IC_AddInk(self.ProjektConversionButton)
			SupposedPath = ProjektFullView().GetProjekt().GetFolder()/self._content
			if SupposedPath.is_dir(): self.ProjektConversionButton.visible = True
			###
			self._mainRow = ft.Row(
				expand= True,
				controls=[
					self._text,
					self.ProjektConversionButton
				]
			)
			###
			super().__init__(
				aspect_ratio=20,
				content=self._mainRow,
				bgcolor= ft.Colors.GREY_500,
				align= ft.Alignment.CENTER,
				padding= ft.Padding(10,0,0,0)
			)

		def mkProjekt(self):
			p.New(
				ProjektFullView().GetProjekt().GetFolder(),
				self._content,
				"",
			)
			ProjektFullView().Reload()
			
	def __init__(self):
		self._LoadedProjekt:p|None = None
		###
		self._tagListColumn = ft.ListView(
			expand=9,
			controls=[],
			spacing=5
		)
		self._newTagButton = ft.Button(
			expand=1,
			content="Add New Tag",
			icon=ft.Icons.ADD,
			align=ft.Alignment.CENTER,
			on_click= lambda evt: TagSelector().Open([
				(
					"Add Tag",
					"#a0f",
					lambda sel: self.AddSelectedTags(sel)
				)
			])
		)
		th.ApplyButtonTheme(self._newTagButton)
		self._ProjektTagList = ft.Column(
			expand=True,
			controls=[
				self._tagListColumn,
				self._newTagButton
			]
		)

		self._taskListColumn = ft.ListView(
			expand=9,
			controls=[],
			spacing=10
		)
		self._newTaskButton = ft.Button(
			expand=1,
			content="Create New Task",
			icon=ft.Icons.ADD,
			align=ft.Alignment.CENTER,
			on_click= lambda evt: self.MkTask()
		)
		th.ApplyButtonTheme(self._newTaskButton)
		self._ProjektTaskList = ft.Column(
			expand=True,
			controls=[
				self._taskListColumn,
				self._newTaskButton
			],
		)

		self._ContentColumn = ft.ListView(
			expand=9,
			controls=[],
			spacing=10
		)
		self._openFolderButton = ft.Button(
			content="Open In File Manager",
			expand=1,
			align=ft.Alignment.CENTER,
			on_click= lambda: self._LoadedProjekt.OpenInExplorer()
		)
		th.ApplyButtonTheme(self._openFolderButton)
		
		self._ContentPage = ft.Column(
			expand=True,
			controls=[
				self._ContentColumn,
				self._openFolderButton
			]
		)

		###
		self._TabsBar = ft.TabBar(
			expand=2,
			tab_alignment= ft.TabAlignment.START,
			tabs= [
				ft.Tab(label="Tags",icon=ft.Icons.TAG),
				ft.Tab(label="Tasks",icon=ft.Icons.CHECK),
				ft.Tab(label="Content",icon=ft.Icons.ARCHIVE_OUTLINED)
			],
			indicator_color= th.ThemeColors["HiltColor"],
			label_color= th.Tint(th.ThemeColors["HiltColor"], 85),
			overlay_color=th.Dim(th.ThemeColors["HiltColor"], 85),
			on_click= self.OnTabChanged
		)
		self._TabViews = ft.TabBarView(
			expand=9,
			controls=[
				self._ProjektTagList,
				self._ProjektTaskList,
				self._ContentPage
			]
		)
		
		###
		self._ProjektTitleEntry = ft.TextField(
			value="",
			label="Projekt Name",
			expand=1,
			input_filter= ft.InputFilter(
				allow=True,
				regex_string= UTIL.FOLDER_REGEX
			)
		)
		th.FTA_Contrast(self._ProjektTitleEntry)


		self._TabStructure = ft.Tabs(
			expand=9,
			length=3,
			content= ft.Column(
				expand=True,
				controls=[
					self._TabsBar,
					self._TabViews
				]
			)
		)

		###
		self._Level1Column = ft.Column(
			expand= True,
			spacing= 5,
			controls=[
				self._ProjektTitleEntry,
				self._TabStructure
			]
		)

		###
		super().__init__(
			content=self._Level1Column,
			padding=ft.Padding(10,10,10,10),
			expand=True,
			visible= False
		)
		th.CTA_Accent(self)
		self.bgcolor = th.Dim(str(self.bgcolor), 85)

	def Load(self,projekt:p):
		if not (self._LoadedProjekt is None): self._LoadedProjekt.Save()
		self.visible = True
		self._LoadedProjekt = projekt
		self._tagListColumn.controls = [
			TagView(
				tag,
				TagView.Form.NORMAL,
				False,
				True,
				False,
				OnRemoveCallback= lambda evt:
					self.TagRemoveCallback(evt.control)
			)
			for tag in projekt.GetTags()
		]
		self._taskListColumn.controls = [
			TaskSimpleView(task)
			for task in projekt.GetTasks()
		]
		self._ProjektTitleEntry.value = projekt.GetName()

	def OnTabChanged(self, evt:ft.Event[ft.TabBar]):
		if self._LoadedProjekt is None: return
		match evt.data:
			case 0: pass
			case 1: pass
			case 2:
				self._ContentColumn.controls = [
					ProjektFullView.ContentUnit(c)
					for c in self._LoadedProjekt.GetContent()
				]

	def AddSelectedTags(self, selected:list[t]):
		self._LoadedProjekt.GetTags().extend([
			tag for tag in selected
			if not (tag in self._LoadedProjekt.GetTags())
		])
		self._tagListColumn.controls = [
			TagView(
				tag,
				TagView.Form.NORMAL,
				False,
				True,
				False,
				OnRemoveCallback= lambda evt:
					self.TagRemoveCallback(evt.control)
			)
			for tag in self._LoadedProjekt.GetTags()
		]

	def MkTask(self):
		if self._LoadedProjekt is None: return
		nT = tk("","","",False)
		self._LoadedProjekt.GetTasks().append(nT)
		self.Reload()
		TaskFullView().Load(nT)
	
	def TagRemoveCallback(self,Caller:TagView):
		self._LoadedProjekt.GetTags().remove(Caller.GetTag())
		self._tagListColumn.controls.remove(Caller)

	def GetProjekt(self):
		return self._LoadedProjekt

	def Reload(self):
		if self._LoadedProjekt is None: return
		self.Load(self._LoadedProjekt)

class TaskSimpleView(ft.Container):

	def __init__(self, task:tk):
		self._task = task
		###
		self.TitleText = ft.Text(
			value= self._task.Name,
			expand=5,
			style= ft.TextStyle()
		)
		self.BulletContainer = ft.Container(
			expand=1,
			aspect_ratio=1,
			content= ft.Icon(ft.Icons.CIRCLE),
			on_click= self.OnBulletClick
		)

		###
		self._level2Row = ft.Row(
			expand=True,
			controls= [
				self.BulletContainer,
				self.TitleText
			]
		)

		###
		self._textContainer = ft.Container(
			expand=8,
			content= self._level2Row,
			on_hover= self.OnHover
		)

		self.EditButton = ft.Container(
			expand=1,
			aspect_ratio=1,
			content= ft.Icon(ft.Icons.EDIT),
			on_click= self.OnFullViewTrigger
		)
		th.IC_AddInk(self.EditButton)

		self.DestroyButton = ft.Container(
			expand=1,
			aspect_ratio=1,
			content= ft.Icon(ft.Icons.DELETE),
			on_click= self.OnDestroy
		)
		th.IC_AddInk(self.DestroyButton)

		###
		self._MainRow = ft.Row(
			expand=True,
			controls= [
				self._textContainer,
				self.EditButton,
				self.DestroyButton
			]
		)

		###
		super().__init__(
			aspect_ratio=10,
			expand_loose=True,
			content= self._MainRow
		)
		th.MockOrnationMode(
			lambda:th.CTA_Contrast(self),
			cf.OrnationModeENUM.CONTOUR
		)

	def OnHover(self, evt:ft.Event[ft.Container]):
		if self._task.Complete: return
		decValue:ft.TextDecoration
		match evt.data:
			case True: decValue = ft.TextDecoration.UNDERLINE
			case False: decValue = ft.TextDecoration.NONE
		self.TitleText.style.decoration = decValue

	def OnBulletClick(self, evt:ft.Event[ft.Container]):
		self._task.Complete = not self._task.Complete
		decValue:ft.TextDecoration
		match self._task.Complete:
			case True: decValue = ft.TextDecoration.LINE_THROUGH
			case False: decValue = ft.TextDecoration.UNDERLINE
		self.TitleText.style.decoration = decValue

	def OnFullViewTrigger(self, evt:ft.Event[ft.Container]):
		TaskFullView().Load(self._task)

	def OnDestroy(self, evt:ft.Event[ft.Container]):
		ProjektFullView().GetProjekt().GetTasks().remove(self._task)
		ProjektFullView().Reload()
				
@UTIL.singleton
class TaskFullView(ft.Container):
	def __init__(self):
		self._loadedTask:tk = None
		###
		self.DeadlineText = ft.TextField(
			value= "",
			expand_loose=True,
			read_only=True,
			prefix= "Deadline: ",
			text_align= ft.TextAlign.RIGHT,
			align= ft.Alignment.CENTER_RIGHT
		)
		th.MockOrnationMode(
			lambda:th.ApplyFieldTheme(
				self.DeadlineText,
					th.ThemeColors["HiltColor"]
			),
			cf.OrnationModeENUM.CONTOUR
		)

		self._IndefiniteDeadlineButton = ft.Container(
			aspect_ratio=1,
			expand_loose=True,
			content=ft.Icon(ft.Icons.CANCEL),
			on_click= lambda evt: self.MakeDeadlineIndefinite()
		)

		self._EditDeadlineButton = ft.Container(
			aspect_ratio=1,
			expand_loose=True,
			content=ft.Icon(ft.Icons.EDIT),
			on_click= lambda evt: self.OpenDeadlineDialog()
		)

		self.QuitButton = ft.Container(
			expand=1,
			aspect_ratio=2,
			bgcolor="#f33",
			align= ft.Alignment.TOP_RIGHT,
			content= ft.Icon(ft.Icons.CLOSE),
			on_click= lambda evt: self.Close()
		)

		self.TitleText = ft.TextField(
			value= "",
			expand=True,
			text_align= ft.TextAlign.LEFT,
			input_filter= ft.InputFilter(
				regex_string=r"[a-zA-Z0-9 ]*"
			),
			label= "Task Name",
			on_change= self.OnTitleChange
		)
		th.MockOrnationMode(
			lambda:th.ApplyFieldTheme(
				self.TitleText,
					th.ThemeColors["HiltColor"]
			),
			cf.OrnationModeENUM.CONTOUR
		)
		

		###
		self._topRow = ft.Row(
			expand=1,
			controls=[
				self.TitleText,
				self.QuitButton
			]
		)
		self._deadlineRow = ft.Row(
			expand=1,
			controls= [
				self.DeadlineText,
				self._IndefiniteDeadlineButton,
				self._EditDeadlineButton
			],
			alignment= ft.MainAxisAlignment.END
		)
		
		self.DescriptionText = ft.TextField(
			value= "",
			expand=5,
			text_align= ft.TextAlign.LEFT,
			multiline=True,
			label= "Description",
			label_style= ft.TextStyle(
				color= th.Tint(th.ThemeColors["HiltColor"],75)
			),
			border= ft.NoInputBorder(),
			on_change= self.OnDescriptionChange
		)
		

		

		###
		self._level1Column = ft.Column(
			expand_loose=True,
			controls= [
				self._topRow,
				self._deadlineRow,
				self.DescriptionText
			],
			tight=True,
		)

		###
		super().__init__(
			expand=True,
			left=30, right=30,
			top=30, bottom=30,
			padding= 15,
			content=self._level1Column,
			visible= False,
		)
		th.MockOrnationMode(
			lambda:th.ApplyContainerTheme(
				self,
					th.ThemeColors["HiltColor"]
			),
			cf.OrnationModeENUM.CONTOUR
		)
		self.bgcolor = th.Dim(th.ThemedBG(), 80)

	def Load(self, task:tk):
		self._loadedTask = task
		self.TitleText.value = task.Name
		self.DescriptionText.value= task.Description

		if self._loadedTask.Deadline == "":
			self.DeadlineText.value = "N/A"
		else: self.DeadlineText.value = self._loadedTask.Deadline
		self.visible = True

	def OnTitleChange(self, evt:ft.Event[ft.TextField]):
		self._loadedTask.Name = evt.data

	def OnDescriptionChange(self, evt:ft.Event[ft.TextField]):
		self._loadedTask.Description = evt.data

	def MakeDeadlineIndefinite(self):
		self._loadedTask.Deadline = ""
		self.DeadlineText.value = "N/A"

	def OpenDeadlineDialog(self):
		inputDate:UTIL.dt
		if self._loadedTask.Deadline == "":
			inputDate = UTIL.dt.today()
		else:
			inputDate = UTIL.dt.fromisoformat(
				self._loadedTask.Deadline
			)
		dp = ft.DatePicker(
			current_date=inputDate,
			first_date= UTIL.dt.today(),
			expand=True,
			on_change= self.OnDeadlineChange,
		)
		MainGrid().GetFullViewArea().controls.append(dp)
		self.page.show_dialog(dp)

	def OnDeadlineChange(self,evt:ft.Event[ft.DatePicker]):
		isoStr = evt.control.value.date().isoformat()
		self._loadedTask.Deadline = isoStr
		self.DeadlineText.value = isoStr
	
	def Close(self):
		ProjektFullView().Reload()
		self.visible = False
#endregion

@UTIL.singleton
class SearchBox(ft.Container):
	def __init__(self):
		###
		self.TagBar = ft.ListView(
			horizontal=True,
			expand=True,
			controls=[],
			spacing=0,
		)

		self.AddTagButton = ft.Container(
			aspect_ratio=1,
			expand=1,
			content=ft.Icon(ft.Icons.ADD),
			bgcolor= ft.Colors.RED,
			on_click= lambda evt: self.PromptTagSelect()
		)

		###
		self.SearchBar = ft.TextField(
			expand=3,
			value="",
			label="Search",
			max_lines=1,
			input_filter= ft.InputFilter(
				allow=True,
				regex_string=UTIL.FOLDER_REGEX,
			)
		)
		th.FTA_Accent(self.SearchBar)

		self._level3Row = ft.Row(
			expand=2,
			controls=[
				ft.Container(
					content=self.TagBar,
					expand= 9,
					border_radius= 10
				),
				self.AddTagButton
			],
			spacing=5
		)

		###
		self._level2Column = ft.Column(
			expand=6,
			controls=[
				self.SearchBar,
				self._level3Row
			],
			spacing=3
		)

		self.SearchButton = ft.Container(
			aspect_ratio=1,
			expand=1,
			content=ft.Icon(ft.Icons.SEARCH),
			on_click= lambda evt: self.Query()
		)
		th.CTA_Contrast(self.SearchButton)

		###
		self._level1Row = ft.Row(
			expand=True,
			controls=[
				self._level2Column,
				self.SearchButton
			]
		)
		
		###
		super().__init__(
			expand=True,
			content=self._level1Row,
			padding=3,
			bgcolor= cf().GetTheme()["FlatColor"]
		)

	def AddTagsToSearch(self, tlist:list[t]):
		currentTagList:list[t] = [view.GetTag() for view in self.TagBar.controls]
		self.TagBar.controls.extend([
			TagView(
				tag,
				TagView.Form.MINI,
				False,
				True,
				False,
				OnRemoveCallback= lambda evt: self.TagBar.controls.remove(evt.control)
			)
			for tag in tlist
			if tag not in currentTagList
		])
		TagSelector().Close()

	def PromptTagSelect(self):
		TagSelector().Open(
			[
				("Add Selected to Search",
					"#a0f",
					self.AddTagsToSearch
				)
			]
		)
	
	def Query(self): 
		tList: list[t] = [view.GetTag() for view in self.TagBar.controls]
		searchString = self.SearchBar.value

		pList: list[p] = Core.Search(
			str(NavigationBar().GetCurrentDir()),
			searchString,
			tList
		)

		ProjektList().DisplayProjekts(pList)

@UTIL.singleton
class NavigationBar(ft.Container):

	class String(ft.ListView):
		def __init__(self, pList:list[UTIL.Path]):
			self.PList = pList
			self.NodeList = []
			for path in pList:
				name = ""
				if path is cf().GetSuperDir():
					name = "Main"
				else: name = p.Load(path).GetName()
				self.NodeList.append(NavigationBar.Node(
					name, path
				))

			super().__init__(
				expand=True,
				controls= self.NodeList,
				horizontal=True,
				padding= 5,
				spacing= 10,
				divider_thickness=2
			)

		def Previous(self):
			return NavigationBar.String(
				self.PList[:-1]
			)

		def GetCurrentDir(self):
			return self.PList[-1]

		def __eq__(self, value: object) -> bool:
			try: assert type(value) == NavigationBar.String
			except AssertionError: raise TypeError()
			sizeCheck = len(self.PList) == len(value.PList)
			if not sizeCheck: return False
			ContentMismatchCheck = False in [
				True
				for i in range(len(self.PList))
				if str(self.PList[i]) == str(value.PList[i])
			]

			return not ContentMismatchCheck

		def __repr__(self) -> str:
			return str(self.PList)

	class Node(ft.Text):
		def __init__(self, name:str, directory:UTIL.Path):
			self.Directory = directory
			super().__init__(
				value=name,
				text_align= ft.TextAlign.CENTER,
				expand=True
			)

	def __init__(self):
		self.history:list[NavigationBar.Node] = []
		self._history:list[NavigationBar.String] = []

		###
		self._parentButton = ft.Container(
			aspect_ratio=1,
			content= ft.Icon(ft.Icons.ARROW_UPWARD),
			expand=True,
			on_click= lambda evt: self.NavOutOfC()
		)
		self._previousButton = ft.Container(
			aspect_ratio=1,
			content= ft.Icon(ft.Icons.ARROW_LEFT),
			expand=True,
			on_click= lambda evt: self.NavBackToPQ()
		)

		###
		self._navRow = ft.Stack(
			expand=6,
			controls=[]
		)
		self._buttonRow = ft.Row(
			aspect_ratio=1,
			expand=2,
			controls=[
				self._parentButton,
				self._previousButton
			]
		)
		###
		self._level1Row = ft.Row(
			expand=True,
			controls=[
				self._navRow,
				self._buttonRow
			]
		)

		###
		super().__init__(
			expand=True,
			content= self._level1Row
		)
		th.ApplyContainerTheme(self,th.ThemeColors["HiltColor"])

	def _update(self):
		self._navRow.controls = self.history
		ProjektList().DisplayProjekts(
			p.CollectFromDir(
				str(self.GetCurrentDir()),
				False
			)
		)
		if p.DefinedAt(self.GetCurrentDir()):
			ProjektFullView().Load(
				p.Load(self.GetCurrentDir())
			)

	def NavInto(self, dir:UTIL.Path):
		s = NavigationBar.String(
			Core.GetProjektChain(dir)
		)
		self._history.append(s)
		self._FinalizeNavigation()

	def NavOutOfC(self):
		current = self.GetCurrentHistory()
		if len(current.PList) <= 1: return
		self._history.append(current.Previous())
		self._FinalizeNavigation()
		

	def NavBackToPQ(self):
		if len(self._history) > 1: self._history.pop()
		self._FinalizeNavigation()
		
	def _FinalizeNavigation(self):
		if len(self._history) > 35: self._history.pop(1)
		## remove already-present equivalent histories
		current = self.GetCurrentHistory()
		cb: list[int] = []
		for i in range(len(self._history) - 1):
			if current == self._history[i]:
				cb.append(i)

		for idx in cb:
			self._history.pop(idx)

		self._navRow.controls = current

		ProjektList().DisplayProjekts(
			p.CollectFromDir(
				str(current.GetCurrentDir()),
				False
			)
		)

		if p.DefinedAt(current.GetCurrentDir()):
			ProjektFullView().Load(p.Load(
				current.GetCurrentDir()
			))



	def ScopeInto(self, label ,dir:UTIL.Path):
		self.history.append(NavigationBar.Node(
			label,
			dir
		))
		self._update()
		
	def ScopeOutOf(self):
		cn = self.history.pop()
		pAuDir = Core.GetParentAugmentedDirectory(cn.Directory)
		print(pAuDir)
		if pAuDir != cf().GetSuperDir():
			#we know it's going to be a projekt, so we load it to get its name
			prjk = p.Load(pAuDir)
			self.ScopeInto(
				prjk.GetName(),
				prjk.GetFolder()
			)
			del prjk
		self._update()

	def ScopeBackTo(self):
		if len(self.history) > 1: self.history.pop()
		self._update()

	def GetCurrentHistory(self):
		return self._history[-1]

	def GetCurrentDir(self):
		return self.history[-1].Directory

@UTIL.singleton
class ProjektList(ft.Container):
	def __init__(self):
		self._MKProjektButton = ft.Button(
			expand=1,
			content= "Create New Projekt",
			icon=ft.Icons.ADD,
			on_click= self.PromptCreateNewProjekt,
			align= ft.Alignment.CENTER
		)
		th.BTA_Accent(self._MKProjektButton)
		self._InnerList = ft.ListView(
			expand=5,
			padding=ft.Padding(20,10,20,10),
			spacing= 20
		)
		###
		self._level1Column = ft.Column(
			expand=True,
			controls=[
				self._InnerList,
				self._MKProjektButton
			]
		)

		###
		super().__init__(
			expand=True,
			padding=10,
			content=self._level1Column
		)
		th.CTA_Contrast(self)
		self.bgcolor = th.Dim(str(self.bgcolor), 85)

	def DisplayProjekts(self,pList:list[p]):
		self._InnerList.controls = [ProjektSimpleView(p) for p in pList]

	def ExtendProjektDisplay(self,pList:list[p]):
		self._InnerList.controls.extend([
			ProjektSimpleView(p) for p in pList
		])

	def PromptCreateNewProjekt(self, evt:ft.Event[ft.Button]):
		ProjektCreator().Open()
#endregion

#region TagEditor
class TagEditor:

	@UTIL.singleton
	class Lister(ft.Container):
		BDESC_TYPE = list[tuple[
			str,
			UTIL.ty.Callable[[ft.Event[ft.Button]], None]
		]]
		def __init__(self):

			self._ButtonDescriptors:TagEditor.Lister.BDESC_TYPE = [
				("+ Create New", lambda evt: self._CreateNew()),
				("Select All", lambda evt: self._ToggleSelectAll(True)),
				("Deselect All", lambda evt: self._ToggleSelectAll(False)),
				("Destroy Selected", lambda evt: self._DestroySelected(evt.control))
			]

			self._destroyAllClicks = 0
			self._destroyDelayedCallback = None
			###

			self._TagViews: list[TagView] = []

			self._tagList = ft.ListView(
				spacing=5,
				expand=7,
			)

			bArr= []
			for tpl in self._ButtonDescriptors:
				b = ft.Button(
					content=tpl[0],
					on_click= tpl[1],
					expand=True,
					align= ft.Alignment.CENTER
				)
				th.ApplyButtonTheme(b,th.ThemeColors["HiltColor"])
				bArr.append(b)
			self._buttonColumn = ft.Column(
				expand=3,
				controls= bArr
			)

			###
			self._level1Column = ft.Column(
				controls= [
					self._tagList,
					self._buttonColumn
				]
			)

			###
			super().__init__(
				expand= True,
				content= self._level1Column,
				padding=10,
				bgcolor=ft.Colors.BLACK,
				visible=False
			)
			th.MockOrnationMode(
				lambda:th.ApplyContainerTheme(
					self,
						th.ThemeColors["HiltColor"]
				),
				cf.OrnationModeENUM.CONTOUR
			)
			self.bgcolor = th.Dim(th.ThemedBG(), 80)

		def LoadTags(self):
			self._TagViews = self._tagList.controls = [
				TagView(
					tag,
					TagView.Form.NORMAL,
					True,
					True,
					True,
					OnEditCallback= lambda evt: TagEditor.Editor().LoadTag(evt.control.GetTag()),
					OnRemoveCallback= lambda evt: self._tagList.controls.remove(evt.control)
				)
				for tag in list(t.Instances.values())
			]

		def _CreateNew(self):
			TagEditor.Editor().LoadTag(t.New("","#777"))

		def _ToggleSelectAll(self, toggle:bool):
			for view in self._TagViews:
				view.Select(toggle)

		def _DestroySelected(self, DestroyButton:ft.Button):
			self._destroyAllClicks += 1
			def Abort():
				print(self._destroyAllClicks)
				if self._destroyAllClicks >= 2: return
				DestroyButton.content = "Not Destroying"
				DestroyButton.update()
				self.page.loop.call_later(
					1,Revert
				)
			
			def Revert():
				self._destroyAllClicks = 0
				DestroyButton.content = "Destroy Selected"
				DestroyButton.update()

			match self._destroyAllClicks:
				case 1:
					DestroyButton.content = "Are you sure? (No Undo)"
					self.page.loop.call_later(1,Abort)
				case 2:
					DestroyButton.content = "Destroying"
					#self._destroyDelayedCallback.cancel()
					self.page.loop.call_later(1,Revert)
					Selection = [
						i 
						for i in range(len(self._TagViews))
						if self._TagViews[i].Selected == True
					]
					for Selected in Selection:
						view = self._TagViews[Selected]
						t.Instances.pop(view.GetTag().identifier)
						self._TagViews.remove(view) # so that the list also clears
					

	@UTIL.singleton
	class Editor(ft.Container):
		def __init__(self):
			self._loadedTag:t = None
			###
			self.TitleField = ft.TextField(
				expand=1,
				label="Tag Name",
				input_filter= ft.InputFilter(r"[a-zA-Z0-9]"),
				filled=True,
				on_change= self.FlushTextChanges
			)
			self.ColorPicker = HexHSVColorPicker(
				on_color_changed= self.FlushColorChanges
			)
			self.ColorPicker.expand = 5
			
			###
			self._mainColumn = ft.Column(
				expand=True,
				controls=[
					self.TitleField,
					self.ColorPicker,
					ft.Container(expand=4)
				]
			)

			###
			super().__init__(
				expand=True,
				content=self._mainColumn,
				bgcolor=ft.Colors.BLACK,
				padding=20,
				visible=False
			)

		def LoadTag(self, tag:t):
			self._loadedTag = tag
			self.TitleField.value = tag.name
			self.TitleField.fill_color = th.taj(tag.color)
			self.ColorPicker.SetWithHex(tag.color)

		def FlushColorChanges(self, evt:ft.Event[HexHSVColorPicker]):
			if not self._loadedTag: return
			self._loadedTag.color = evt.data
			self.TitleField.fill_color = th.taj(str(evt.data))
			try: self.update() 
			except RuntimeError: pass

		def FlushTextChanges(self,evt:ft.Event[ft.TextField]):
			if not self._loadedTag: return
			self._loadedTag.name = evt.data
	
#endregion

#region SettingsEditor
@UTIL.singleton
class SettingsEditor(ft.Container):
	ready = False

	class SettingEntry(ft.Container):
		def __init__(
			self,
			MainLabel:str,
			DullLabel:str,
		):
			self.LabelText = ft.TextField(
				value= MainLabel,
				expand=True,
				read_only=True,
				border= ft.NoInputBorder(),
				label=DullLabel
			)
			###
			self._SettingRow = ft.Row(
				expand=True,
				controls=[
					self.LabelText
				],
				vertical_alignment=ft.CrossAxisAlignment.START
			)
			###
			super().__init__(
				expand=True,
				content=self._SettingRow
			)

		def Replicate(self): pass
			#if not SettingsEditor.ready: return
			#SettingsEditor().WriteSettings()

	class TextEntry(SettingEntry):
		def __init__(self, MainLabel:str, DullLabel:str):
			super().__init__(MainLabel,DullLabel)
			self._Entry = ft.TextField(
				value="",
				input_filter=ft.InputFilter(UTIL.PATH_REGEX),
				expand=True,
			)
			self._SettingRow.controls.append(self._Entry)
			self.value = ""

		def SetValue(self, v:str):
			self.value = self._Entry.value = v
			self.Replicate()

	class RotateEntry(SettingEntry):
		def __init__(self, MainLabel:str, DullLabel:str):
			super().__init__(MainLabel,DullLabel)
			self._Entry = ft.Button(
				content="",
				on_click= lambda evt: self.SetValue(self.value+1),
				expand=True
			)
			th.ApplyButtonTheme(
				self._Entry,
				th.Tint(th.ThemeColors["FlatColor"],60)
			)
			self._SettingRow.controls.append(self._Entry)
			self.value = 1

		def SetValue(self, v:int):
			if v > 3: v = 1
			self.value= v
			self._Entry.content = cf.OrnationModeENUM._member_names_[v-1]
			self.Replicate()
	
	class ThemeColorEntry(SettingEntry):
		def __init__(self, ColorLabel:str, DullLabel:str):
			super().__init__(ColorLabel,DullLabel)
			self.CurrentColor = ""

			self.ColorPickerContainer = ft.ExpansionTile(
				title="",
				expand=True
			)

			self.ColourPicker = HexHSVColorPicker(
				on_color_changed= lambda evt: self.SetColor(str(evt.data))
			)
			self.ColorPickerContainer.controls = [self.ColourPicker]

			self._SettingRow.controls.append(self.ColorPickerContainer)

		def SetColor(self, col:str):
			self.CurrentColor = col
			self.ColorPickerContainer.collapsed_bgcolor = self.CurrentColor
			self.ColorPickerContainer.bg = self.CurrentColor
			self.Replicate()

		def OverrideColor(self,col:str):
			self.ColourPicker.SetWithHex(col)
			
	def __init__(self):
		self.SuperDirEntry = SettingsEditor.TextEntry(
			"Super-Directory",
			"Projekt Parent Folder"
		)
		self.SuperDirEntry.SetValue(str(cf().GetSuperDir()))

		self.FlatColorEntry = SettingsEditor.ThemeColorEntry(
			"Flat Color",
			"Background Color"
		)
		self.FlatColorEntry.OverrideColor(cf().GetTheme()["FlatColor"])

		self.EdgeColorEntry = SettingsEditor.ThemeColorEntry(
			"Edge Color",
			"Accent Color"
		)
		self.EdgeColorEntry.OverrideColor(cf().GetTheme()["EdgeColor"])

		self.GuardColorEntry = SettingsEditor.ThemeColorEntry(
			"Guard Color",
			"Contrast Color"
		)
		self.GuardColorEntry.OverrideColor(cf().GetTheme()["GuardColor"])

		self.HiltColorEntry = SettingsEditor.ThemeColorEntry(
			"Hilt Color",
			"Selection Color"
		)
		self.HiltColorEntry.OverrideColor(cf().GetTheme()["HiltColor"])

		self.OrnationModeEntry = SettingsEditor.RotateEntry(
			"Ornation Mode",
			"Colour Arrangement"
		)
		self.OrnationModeEntry.SetValue(cf().GetTheme()["OrnationMode"])

		self.ApplyButton = ft.Button(
			content="Apply",
			on_click= self.WriteSettings
		)
		th.ApplyButtonTheme(self.ApplyButton)
		
		###
		self._settingsList = ft.ListView(
			expand=True,
			controls=[
				self.SuperDirEntry,
				self.FlatColorEntry,
				self.EdgeColorEntry,
				self.GuardColorEntry,
				self.HiltColorEntry,
				self.OrnationModeEntry,
				self.ApplyButton
			],
			spacing=10
		)

		###
		super().__init__(
			bgcolor= ft.Colors.BLACK,
			content= self._settingsList,
			expand=True,
			visible=False,
			padding=30,
		)
		SettingsEditor.ready = True
	
	async def WriteSettings(self) -> None:
		cf().SetSuperDir(self.SuperDirEntry.value)
		cf().GetTheme().update(
			FlatColor= self.FlatColorEntry.CurrentColor,
			EdgeColor= self.EdgeColorEntry.CurrentColor,
			GuardColor= self.GuardColorEntry.CurrentColor,
			HiltColor= self.HiltColorEntry.CurrentColor,
			OrnationMode= cf.OrnationModeENUM(self.OrnationModeEntry.value) 
		)
		await RestartApp()

#endregion

#region GlobalUI
@UTIL.singleton
class EditorSwitcher(ft.Container):
	def __init__(self):
		self._state = -1
		self._icon = ft.Icon(ft.Icons.NO_CELL_OUTLINED)
		super().__init__(
			expand= True,
			ink= True,
			on_click= lambda evt: self.CycleState(),
			content=self._icon
		)
		th.MockOrnationMode(
			lambda: th.ApplyContainerTheme(
				self,
				th.ThemeColors["HiltColor"]
			),
			cf.OrnationModeENUM.UNBOUND
		)
		self.CycleState()

	def CycleState(self):
		self._state = (self._state + 1) % 3

		match self._state:
			case 0:
				self._icon.icon = ft.Icons.ARCHIVE_OUTLINED
				self.ToggleConfig(False)
				self.ToggleTag(False)
				self.ToggleProjekt(True)
				
			case 1:
				self._icon.icon = ft.Icons.LABEL_OUTLINED
				self.ToggleConfig(False)
				self.ToggleProjekt(False)
				self.ToggleTag(True)
				TagEditor.Lister().LoadTags()

			case 2:
				self._icon.icon = ft.Icons.SETTINGS_OUTLINED
				self.ToggleTag(False)
				self.ToggleProjekt(False)
				self.ToggleConfig(True)

	def ToggleProjekt(self, t:bool):
		SearchBox().visible = t
		NavigationBar().visible = t
		ProjektList().visible = t
		ProjektFullView().visible = t

		if t == False:
			TaskFullView().visible = False
			TagSelector().Close()
			ProjektCreator().Close()

	def ToggleTag(self, t:bool):
		TagEditor.Lister().visible = t
		TagEditor.Editor().visible = t

	def ToggleConfig(self, t:bool):
		SettingsEditor().visible = t

@UTIL.singleton
class MainGrid(ft.Container):
	def __init__(self):
		print("Ante Up!")
		###
		self.searchBarArea = ft.Container(
			expand=True,
			bgcolor= ft.Colors.GREY
		)

		self._configButtonArea = ft.Container(
			bgcolor= ft.Colors.GREY,
			aspect_ratio=1
		)

		###
		self._FullViewArea = ft.Stack(
			expand=True,
			controls= [
				ft.Container(
					expand=True,
					bgcolor= ft.Colors.GREY
				)
			]
		)

		self._Level3Row1 = ft.Row(
			expand=3,
			controls=[
				self._configButtonArea,
				self.searchBarArea
			]
		)

		self._NavigationBarArea = ft.Container(
			expand=1,
			content=None,
			bgcolor= ft.Colors.GREY
		)

		self._ListArea = ft.Stack(
			expand=16,
			controls= [
				ft.Container(
					expand=True,
					bgcolor= th.ThemeColors["FlatColor"]
				)
			]
		) 

		###
		self._Level2ColumnLeft = ft.Column(
			expand=1,
			controls=[
				self._Level3Row1,
				self._NavigationBarArea,
				self._ListArea
			]
		)

		self._Level2ColumnRight = ft.Column(
			expand=2,
			controls=[
				self._FullViewArea
			]
		)

		###
		self._Level1Row = ft.Row(
			expand=True,
			controls=[
				self._Level2ColumnLeft,
				self._Level2ColumnRight
			]
		)

		###
		super().__init__(
			content= self._Level1Row,
			expand=True
		)

	def GetConfigButtonArea(self):
		return self._configButtonArea

	def GetSearchBarArea(self):
		return self.searchBarArea

	def GetNavigationBarArea(self):
		return self._NavigationBarArea

	def GetListArea(self):
		return self._ListArea

	def GetFullViewArea(self):
		return self._FullViewArea
#endregion

class ShutdownMode(UTIL.IntEnum):
	PENDING_RESTART= 2
	PERMANENT_SHUTDOWN = 3
	

ChosenSM:ShutdownMode = ShutdownMode.PERMANENT_SHUTDOWN

window:ft.Window

def main(page:ft.Page):
	global window
	MainGrid().GetConfigButtonArea().content = EditorSwitcher()
	MainGrid().GetSearchBarArea().content = SearchBox()
	MainGrid().GetNavigationBarArea().content = NavigationBar()
	MainGrid().GetListArea().controls.extend([
		ProjektList(),
		ProjektCreator(),
		TagSelector(),

		TagEditor.Lister()
	])
	MainGrid().GetFullViewArea().controls.extend([
		ProjektFullView(),
		TaskFullView(),

		TagEditor.Editor(),

		SettingsEditor()
	])

	NavigationBar().NavInto(
		cf().GetSuperDir()
	)
	
	page.add(MainGrid())

	window = page.window	
	window.resizable = False

	#page.on_close = lambda: RestartApp()
	

def Render():
	global ChosenSM; ChosenSM = ShutdownMode.PERMANENT_SHUTDOWN
	ft.run(main)

async def RestartApp():
	global ChosenSM; ChosenSM = ShutdownMode.PENDING_RESTART
	TaskFullView.Destroy()
	TagSelector.Destroy()
	TagEditor.Lister.Destroy()
	TagEditor.Editor.Destroy()
	ProjektFullView.Destroy()
	ProjektList.Destroy()
	ProjektCreator.Destroy()
	NavigationBar.Destroy()
	SearchBox.Destroy()
	EditorSwitcher.Destroy()
	SettingsEditor.Destroy()
	MainGrid.Destroy()
	await window.close()
	
	

if __name__ == "__main__": Render()
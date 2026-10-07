from Core import Settings
import flet as ft

import Utilities as UTIL

ThemeColors = Settings().GetTheme()

class ThemeMode(UTIL.IntEnum):
	LIGHT = 1
	DARK = 2

CurrentTheme:ThemeMode

def DetermineTheme():
	global CurrentTheme
	fc = UTIL.colorist.Color(ThemeColors['FlatColor'])
	if fc.get_luminance() > 0.5: CurrentTheme = ThemeMode.LIGHT
	else: CurrentTheme = ThemeMode.DARK
	return CurrentTheme

def Opposite():
	global CurrentTheme
	match CurrentTheme:
		case ThemeMode.LIGHT: return ThemeMode.DARK
		case ThemeMode.DARK: return ThemeMode.LIGHT

def MockTheme(f:UTIL.ty.Callable, th:ThemeMode|None = None):
	global CurrentTheme
	if th is None: th = Opposite()
	original = CurrentTheme
	CurrentTheme = th
	result = f()
	CurrentTheme = original
	return result

def MockOrnationMode(f:UTIL.ty.Callable, om:Settings.OrnationModeENUM):
	original = ThemeColors['OrnationMode']
	ThemeColors['OrnationMode'] = om
	result = f()
	ThemeColors['OrnationMode'] = original
	return result

# Theme Adjust
def taj(col:str):
		"""
		Theme Adjust: \n
		Adjusts the given color to fit the current theme,
		by modifying its luminance. \n
		Where the color's original luminance is at 0.5, 0.1 is added/subtracted depending on theme.
		"""
		color = UTIL.colorist.Color(col)
		value = color.get_luminance()

		if value > 0.4 and value < 0.6:
			match CurrentTheme:
				case ThemeMode.LIGHT: value = 0.4
				case ThemeMode.DARK: value = 0.6

		diff = (0.5 - value)

		modifier = 0
		match CurrentTheme:
			case ThemeMode.LIGHT:
				if diff > 0: modifier = 1

			case ThemeMode.DARK:
				if diff < 0: modifier = -1

		color.set_luminance(value + modifier * 2 * abs(diff))

		return color.get_hex_l()

def Tint(col:str, intensity:int = 20):
	intensity = int(UTIL.Clamp(intensity,0,100))
	color = UTIL.colorist.Color(taj(col))

	modifier = 0
	match CurrentTheme:
		case ThemeMode.LIGHT: modifier = -1
		case ThemeMode.DARK: modifier = 1

	color.set_luminance(UTIL.Clamp(
		color.get_luminance() * (1 + (modifier * intensity/100)),
		0,1
	))

	return color.get_hex_l()

def Dim(col:str, intensity:int = 20):
	return MockTheme(lambda: Tint(col,intensity))
	

def ThemedBG():
	return taj(ThemeColors['FlatColor'])


def Neu(col:str):
	"""
	Neutralise:
	Uses RGB Decomposition to return a grayscale version of the color.
	"""
	color = UTIL.colorist.Color(col)
	Median =  list(color.get_rgb())
	Median.sort()
	Median = Median[1]
	return UTIL.colorist.rgb2hex((Median,)*3, True)
	

def IC_AddInk(Target:ft.Container, Color:str = ThemeColors['HiltColor']):
	Target.ink = True
	Target.ink_color = "80" + Tint(Color)

def ApplyContainerTheme(Target:ft.Container, Color:str):
	match ThemeColors['OrnationMode']:
		case Settings.OrnationModeENUM.UNBOUND:
			Target.bgcolor = taj(Color)
			Target.border = None

		case Settings.OrnationModeENUM.BOUND:
			Target.bgcolor = taj(Color)
			bs = ft.BorderSide(
				width= 3,
				color= Dim(Color),
				stroke_align= ft.BorderSideStrokeAlign.CENTER
			)
			Target.border = ft.Border(*([bs] * 4))

		case Settings.OrnationModeENUM.CONTOUR:
			Target.bgcolor = taj(Neu(Color))
			bs = ft.BorderSide(
				width= 3,
				color= Dim(Color),
				stroke_align= ft.BorderSideStrokeAlign.CENTER
			)
			Target.border = ft.Border(*([bs] * 4))

def CTA_Accent(t:ft.Container):
	ApplyContainerTheme(t,ThemeColors['EdgeColor'])

def CTA_Contrast(t:ft.Container):
	ApplyContainerTheme(t,ThemeColors["GuardColor"])

def ApplyFieldTheme(Target:ft.FormFieldControl, Color:str):
	Target.label_style = ft.TextStyle(
		color= "#ffffff",
		decoration= ft.TextDecoration.UNDERLINE
	)
	match ThemeColors['OrnationMode']:
		case Settings.OrnationModeENUM.UNBOUND:
			Target.bgcolor = taj(Color)
			Target.border = ft.NoInputBorder()

		case Settings.OrnationModeENUM.BOUND:
			Target.bgcolor = taj(Color)
			Target.border = {
				ft.ControlState.DEFAULT: ft.OutlineInputBorder(side=ft.BorderSide(
					width=1,
					color= Tint(Neu(Color))
				)),
			 	ft.ControlState.FOCUSED: ft.OutlineInputBorder(side=ft.BorderSide(
					width=3,
					color= Tint(Color)
				)),
			 	ft.ControlState.DISABLED: ft.OutlineInputBorder(side=ft.BorderSide(
			 		width=3,
			 		color= Tint(Neu(Dim(Color)))
			 	)),
			}

		case Settings.OrnationModeENUM.CONTOUR:
			Target.bgcolor = taj(Neu(Color))
			Target.border = {
				ft.ControlState.DEFAULT: ft.OutlineInputBorder(side=ft.BorderSide(
					width=1,
					color= Tint(Neu(Color))
				)),
				 ft.ControlState.FOCUSED: ft.OutlineInputBorder(side=ft.BorderSide(
					width=3,
					color= Tint(Color)
				)),
				ft.ControlState.DISABLED: ft.BorderSide(
					width=3,
					color= Tint(Neu(Dim(Color)))
				)
			}

def FTA_Accent(t:ft.FormFieldControl):
	ApplyFieldTheme(t,ThemeColors['EdgeColor'])

def FTA_Contrast(t:ft.FormFieldControl):
	ApplyFieldTheme(t,ThemeColors['GuardColor'])

def ApplyButtonTheme(Target:ft.Button, Color:str = ThemeColors['HiltColor']):
	Target.style = ft.ButtonStyle(
		color= Tint(Color, 90),
		bgcolor= {
			ft.ControlState.DEFAULT: Dim(taj(Color),50),
			ft.ControlState.HOVERED: Dim(Neu(Color),50),
			ft.ControlState.PRESSED: Tint(Color, 90)
		} 
	)

def BTA_Accent(Target:ft.Button):
	ApplyButtonTheme(Target, ThemeColors['EdgeColor'])
def BTA_Contrast(Target:ft.Button):
	ApplyButtonTheme(Target, ThemeColors['GuardColor'])



DetermineTheme()
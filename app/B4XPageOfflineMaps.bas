B4A=true
Group=Default Group
ModulesStructureVersion=1
Type=Class
Version=14
@EndOfDesignText@
' Pagina elenco cartografie offline OSCACCIA.
' La pagina viene riutilizzata separatamente nei progetti Capo e Cacciatore.

Sub Class_Globals
	Private Root As B4XView
	Private lblTitle As Label
	Private lblInfo As Label
	Private lblFooter As Label
	Private btnBack As Button
	Private lvMaps As ListView
	Private CatalogJson As String = ""
	Private CallerObject As Object
	Private CallerPageID As String = ""
End Sub

Public Sub Initialize(Caller As Object, BackPageID As String)
	CallerObject = Caller
	CallerPageID = BackPageID
End Sub

Private Sub B4XPage_Created(Root1 As B4XView)
	Root = Root1
	Root.Color = Colors.RGB(238, 242, 239)
	B4XPages.SetTitle(Me, "Mappe offline")

	btnBack.Initialize("btnBack")
	btnBack.Text = "INDIETRO"
	btnBack.TextSize = 13
	Root.AddView(btnBack, 12dip, 12dip, 96dip, 42dip)

	lblTitle.Initialize("")
	lblTitle.Text = "MAPPE OFFLINE"
	lblTitle.TextSize = 20
	lblTitle.Typeface = Typeface.DEFAULT_BOLD
	lblTitle.TextColor = Colors.RGB(35, 75, 48)
	lblTitle.Gravity = Gravity.CENTER_VERTICAL
	Root.AddView(lblTitle, 120dip, 12dip, Max(100dip, Root.Width - 132dip), 42dip)

	lblInfo.Initialize("")
	lblInfo.Text = "Elenco delle aree cartografiche presenti nel catalogo."
	lblInfo.TextSize = 13
	lblInfo.TextColor = Colors.DarkGray
	lblInfo.Gravity = Gravity.CENTER_VERTICAL
	Root.AddView(lblInfo, 14dip, 62dip, Root.Width - 28dip, 42dip)

	lvMaps.Initialize("lvMaps")
	lvMaps.Color = Colors.White
	lvMaps.TwoLinesLayout.Label.TextSize = 17
	lvMaps.TwoLinesLayout.Label.TextColor = Colors.RGB(35, 55, 40)
	lvMaps.TwoLinesLayout.SecondLabel.TextSize = 12
	lvMaps.TwoLinesLayout.SecondLabel.TextColor = Colors.DarkGray
	Root.AddView(lvMaps, 10dip, 108dip, Root.Width - 20dip, Max(100dip, Root.Height - 158dip))

	lblFooter.Initialize("")
	lblFooter.Text = "Tocca una mappa per vedere lo stato o avviare il download."
	lblFooter.TextSize = 12
	lblFooter.TextColor = Colors.DarkGray
	lblFooter.Gravity = Gravity.CENTER
	Root.AddView(lblFooter, 10dip, Root.Height - 44dip, Root.Width - 20dip, 34dip)
End Sub

Private Sub B4XPage_Appear
	If lvMaps.IsInitialized Then RefreshMapList
End Sub

Public Sub SetCatalogJson(JsonText As String)
	CatalogJson = JsonText
	If lvMaps.IsInitialized Then RefreshMapList
End Sub

Private Sub RefreshMapList
	Try
		lvMaps.Clear
		If CatalogJson.Trim = "" Then
			lblInfo.Text = "Catalogo non ancora caricato."
			Return
		End If

		Dim Parser As JSONParser
		Parser.Initialize(CatalogJson)
		Dim Catalog As Map = Parser.NextObject
		Dim MapsList As List = Catalog.Get("maps")
		If MapsList.IsInitialized = False Or MapsList.Size = 0 Then
			lblInfo.Text = "Il catalogo non contiene mappe."
			Return
		End If

		For Each Entry As Map In MapsList
			Dim MapName As String = Entry.GetDefault("name", Entry.GetDefault("id", "Mappa"))
			Dim Country As String = Entry.GetDefault("country", "")
			Dim Region As String = Entry.GetDefault("region", "")
			Dim MapStatus As String = Entry.GetDefault("status", "planned")
			Dim DownloadURL As String = Entry.GetDefault("download_url", "")
			Dim StatusText As String
			If MapStatus = "available" And DownloadURL.StartsWith("https://") Then
				StatusText = "DISPONIBILE - tocca per scaricare"
			Else
				StatusText = "IN PREPARAZIONE - download non ancora attivo"
			End If
			Dim FirstLine As String = MapName
			If Country <> "" Then FirstLine = FirstLine & " - " & Country
			If Region <> "" And Region <> MapName Then FirstLine = FirstLine & " - " & Region
			lvMaps.AddTwoLines2(FirstLine, StatusText, Entry)
		Next

		lblInfo.Text = "Aree cartografiche nel catalogo: " & MapsList.Size
		lblFooter.Text = "Le aree in preparazione sono visibili ma non ancora scaricabili."
	Catch
		lvMaps.Clear
		lblInfo.Text = "Errore nella lettura del catalogo."
		lblFooter.Text = LastException.Message
		Log("MAPPE OFFLINE: " & LastException.Message)
	End Try
End Sub

Private Sub lvMaps_ItemClick(Position As Int, Value As Object)
	If Value = Null Then Return
	Dim SelectedMap As Map = Value
	Dim MapName As String = SelectedMap.GetDefault("name", "Mappa")
	Dim Country As String = SelectedMap.GetDefault("country", "")
	Dim MapStatus As String = SelectedMap.GetDefault("status", "planned")
	Dim DownloadURL As String = SelectedMap.GetDefault("download_url", "")

	If MapStatus <> "available" Or DownloadURL.StartsWith("https://") = False Then
		MsgboxAsync(MapName & " - " & Country & ": pacchetto cartografico ancora in preparazione. Il download sara' attivato quando il file MBTiles sara' pubblicato e verificato.", "MAPPA IN PREPARAZIONE")
		Return
	End If

	B4XPages.ShowPage(CallerPageID)
	CallSubDelayed2(CallerObject, "ProcessOfflineMapSelection", SelectedMap)
End Sub

Private Sub btnBack_Click
	B4XPages.ShowPage(CallerPageID)
End Sub

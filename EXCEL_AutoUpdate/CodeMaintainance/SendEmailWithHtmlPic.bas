Attribute VB_Name = "Module1"
Sub 按鈕1_Click()
'
' 按鈕1_Click 巨集
' 將CSV分隔成excel可吃的格式
'

'
    Columns("A:A").Select
    Selection.TextToColumns Destination:=Range("A1"), DataType:=xlDelimited, _
        TextQualifier:=xlDoubleQuote, ConsecutiveDelimiter:=False, Tab:=True, _
        Semicolon:=False, Comma:=True, Space:=False, Other:=False, FieldInfo _
        :=Array(Array(1, 1), Array(2, 1), Array(3, 1), Array(4, 1), Array(5, 1), Array(6, 1), _
        Array(7, 1), Array(8, 1), Array(9, 1), Array(10, 1), Array(11, 1), Array(12, 1), Array(13, 1 _
        ), Array(14, 1), Array(15, 1)), TrailingMinusNumbers:=True
    Columns("B:B").ColumnWidth = 9.88
    Columns("C:C").EntireColumn.AutoFit
    Columns("D:D").EntireColumn.AutoFit
    Columns("E:E").EntireColumn.AutoFit
    Columns("G:G").EntireColumn.AutoFit
    Columns("H:H").EntireColumn.AutoFit
    Columns("I:I").EntireColumn.AutoFit
    Columns("J:J").EntireColumn.AutoFit
End Sub

Sub PDF()

With Sheet2
Range("A1:H161").Select
ActiveWindow.SelectedSheets.PrintOut Copies:=1, ActivePrinter:="Bullzip PDF Printer", Collate:=True   '設定印表機並列印
End With
    
End Sub

Sub CollectDataFromAutoFilter()
'Frng 是要copy的物件
'xE 是準備貼上的目的地
Dim Frng As Range, xE As Range, Frng2 As Range
Dim j As Integer

Sheets("maillist").Activate
n = Application.WorksheetFunction.CountA(Range("N1", "N1000"))

For j = 2 To n
    CPPH = Sheets("maillist").Cells(j, "N") '篩選營業員
    mail = Sheets("maillist").Cells(j, "O")   '營業員mail
    'compute
    K = CPPH
          
    Sheets("input").Activate
    Sheets("input").Range("$A$2:$M$200").AutoFilter Field:=13, Criteria1:= _
              "=*" + K + "*", Operator:=xlAnd
              
    Set Frng = Sheets("input").AutoFilter.Range.Offset(1, 0)                    '篩選範圍整個往下平移一列
    'Set Frng2 = Sheets("8").Cells(j, 2).Resize(1, 3)
    
      
    Set Frng = Frng.SpecialCells(xlCellTypeVisible) '選取 所有可見儲存格 的某個cell(i,j) 或 row(i)
    Set xE = Sheets("sendtext").Cells(Rows.Count, 1).End(xlUp)                     'Cells(Rows.Count, 1)->第一欄最後一列.End(xlUp) ctrl+UP
    
    
    If xE.Row = 1 Or xE <> "" Then Set xE = xE                            'xE = xE(3,2)平移寫法 下移2右移1
      
    Frng.Copy xE(2)

    Call Sent(mail, j)
    
    
    Sheets("sendtext").Activate
    Rows("2:260").Select
    Selection.Delete Shift:=xlUp
Next j

End Sub

Sub List()
Dim filename As String
Dim rng As Range
Dim WorkRng As Range
Dim Sigh As String
Dim n As Integer
On Error Resume Next

Sheet2.Range("M:M").ClearContents

'開檔
'filename = "\\10.36.205.170\法人部\19.策略訊號及資訊日報\分組清單.xlsx"
filename = "\\10.36.205.170\公用資料夾\統一期貨日報\分組清單.xlsx"
Workbooks.Open filename

'策略訊號發送日報 !!! 這裡才是設定email 的位置
Workbooks("分組清單.xlsx").Sheets("投組").Range("B:B").Copy
Workbooks("統一期貨日報.xls").Sheets("OutPut").Range("M1").PasteSpecial

'關閉檔案
filename = "分組清單.xlsx"
Application.DisplayAlerts = False
Workbooks(filename).Close

n = Application.WorksheetFunction.CountA(Sheet2.Range("M:M"))

'合併收件人並加入分隔;號
Set WorkRng = Sheet2.Range("M1:M" & n)
xOut = ""
Application.DisplayAlerts = False
For Each rng In WorkRng
xOut = xOut & rng.Value & ";"
Next
With WorkRng
.Merge
.Value = VBA.Left(xOut, VBA.Len(xOut) - 1)
End With
Application.DisplayAlerts = True

End Sub
Sub Sent(mail, sr As Integer)
Dim Price, Date1 As String '內文的變數設定為字串
Dim PIC As Range

On Error Resume Next
With Sheet2
    e_mail$ = Trim(mail)   '取得寄出Mail address From Module list
    Date1 = "即將到期之期顧客戶，請協助聯繫續約（如已續約無須理會）謝謝！"
    Price = "詳見附件檔案"
    If e_mail$ = "" Then Beep: Exit Sub
    
    Set app_OL = CreateObject("outlook.Application")
    Set it = app_OL.CreateItem(olMailItem)
    Set atc = it.Attachments
    olByValue = 1
    
    Call ConvertHTMLToImage(Sheet3.Range("A1:M163"), sr)
    
'    With it
    '.To = e_mail$    '收件人
    it.BCC = e_mail$    '密件副本
    it.Subject = Date1 '主旨
    it.Body = Price  '不設定body,可以附上outlook預設簽名檔
    it.HTMLBody = "<html><body><img src='cid:myImage'></body></html>" 'RangetoHTML(Sheet3.Range("A1:M63"))
    
    '插入圖片
    Dim strImage As String
    strImage = Environ("USERPROFILE") & "\Pictures\" & CStr(sr) & ".png" '"C:\Users\09192\Pictures\D.png"
    Dim olAttachment As Object
    Set olAttachment = it.Attachments.Add(strImage, olEmbeddeditem, 0)
    olAttachment.PropertyAccessor.SetProperty "http://schemas.microsoft.com/mapi/proptag/0x3712001F", "myImage"
    
    it.Display
'    End With

    If MsgBox("繼續下一封", vbYesNo) = vbNo Then

    Else
        
'        it.Send
'        MailPMCB11.Enabled = True
        it.Release
'        Sheet2.Range("K4") = Now() & Sheet2.Range("L1") '提示訊息顯示在儲存格
    End If
End With
End Sub

Public Function RangetoHTML(rng As Range)
    Dim fso As Object

    Dim ts As Object
    Dim TempFile As String
    Dim TempWB As Workbook
    Dim rng2 As Range
    
    Dim objStream, strData
    

    TempFile = Environ$("temp") & "/" & Format(Now, "dd-mm-yy h-mm-ss") & ".htm"
 
    rng.Copy
    'MsgBox (rng)
    Set TempWB = Workbooks.Add(1)
    With TempWB.Sheets(1)
        .Cells(1).PasteSpecial Paste:=8
        .Cells(1).PasteSpecial xlPasteValues, , False, False
        .Cells(1).PasteSpecial xlPasteFormats, , False, False
        .Cells(1).Select
        Application.CutCopyMode = False
        On Error Resume Next
        .DrawingObjects.Visible = True
        .DrawingObjects.Delete
        On Error GoTo 0
    End With
 
    With TempWB.PublishObjects.Add(SourceType:=xlSourceRange, filename:=TempFile, Sheet:=TempWB.Sheets(1).name, Source:=TempWB.Sheets(1).UsedRange.Address, HtmlType:=xlHtmlStatic)
        .Publish (True)
    End With
 
    

   ' Set rng2 = TempWB.Sheets(1).UsedRange '指定的範圍
   ' With rng2.Select
   'Set Rng = Selection      '滑鼠選定的範圍
   ' rng2.CopyPicture
   ' With TempWB.Sheets(1).ChartObjects.Add(1, 1, rng2.Width, rng2.Height)  '新增 圖表
   '     .Chart.Paste                                           '貼上 圖片
   '     .Chart.Export filename:="d:\" & Format(Date, "yyyymmdd") & " 統一期貨日報.jpg" '匯出 圖片
        '.Delete                                                '刪除 圖表
   ' End With
   ' End With
    
    'RangetoHTML = TempWB.Sheets(1).ChartObjects
    'MsgBox (RangetoHTML)
    
'
'    Set objStream = CreateObject("ADODB.Stream")
'    objStream.Charset = "utf-8"
'    objStream.Open
'    objStream.LoadFromFile (TempFile)
    
    'Set fso = CreateObject("Scripting.FileSystemObject")
    'Set ts = fso.GetFile(TempFile).OpenAsTextStream(1, 0)
    'Set ts = fso.OpenTextFile(TempFile)
    'RangetoHTML = ts.ReadAll
    WordDoc.Content.InsertAfter GetHTMLBody("TempFile")
    imgFile = "C:\Users\09192\Pictures\D.png"

    
'    RangetoHTML = objStream.ReadText()
    
    'MsgBox (RangetoHTML)
    'ts.Close
'    objStream.Close
'    Set objStream = Nothing
    'MsgBox (ts)
    'RangetoHTML = Replace(RangetoHTML, "align=center x:publishsource=", _
    '                      "align=left x:publishsource=")
 
    TempWB.Close savechanges:=False
    'MsgBox (RangetoHTML)
Kill TempFile

'Set ts = Nothing
    Set fso = Nothing
    Set TempWB = Nothing
    '''
End Function

Function GetHTMLBody(ByVal url As String) As String
    Dim fso As Object, ts As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set ts = fso.OpenTextFile(url)
    GetHTMLBody = ts.ReadAll()
    ts.Close
End Function

Sub ConvertHTMLToImage(rng As Range, sr As Integer)

    Dim fso As Object
    Dim ts As Object
    Dim TempFile As String
    Dim TempWB As Workbook
    Dim rng2 As Range
    
    Dim objStream, strData
    'Format(Now, "dd-mm-yy h-mm-ss")

    TempFile = Environ$("temp") & "\" & "A" & ".html"
 
    rng.Copy
    'MsgBox (rng)
    Set TempWB = Workbooks.Add(1)
    With TempWB.Sheets(1)
        .Cells(1).PasteSpecial Paste:=8
        .Cells(1).PasteSpecial xlPasteValues, , False, False
        .Cells(1).PasteSpecial xlPasteFormats, , False, False
        .Cells(1).Select
        Application.CutCopyMode = False
        On Error Resume Next
        .DrawingObjects.Visible = True
        .DrawingObjects.Delete
        On Error GoTo 0
    End With
 
    With TempWB.PublishObjects.Add(SourceType:=xlSourceRange, filename:=TempFile, Sheet:=TempWB.Sheets(1).name, Source:=TempWB.Sheets(1).UsedRange.Address, HtmlType:=xlHtmlStatic)
        .Publish (True)
    End With


    Dim shell As Object
    Dim path As String
    'Dim url As String
    'Dim imgFile As String
    Dim inputFilePath As String
    Dim outputFilePath As String
    Dim wkhtmltoimagePath As String
    Dim command As String

    Set shell = CreateObject("WScript.Shell")

    ' 設置 HTML 網頁的 URL 和要輸出的圖像檔案名稱和路徑
    'url = "http://www.example.com"
    inputFilePath = TempFile
    outputFilePath = Environ("USERPROFILE") & "\Pictures\" & CStr(sr) & ".png" 'Environ$("temp") & "\" & "A" & ".html"
    

    ' 調用 wkhtmltoimage 工具來將 HTML 轉換為圖像
    path = "C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe"
    ' 构建命令行命令
    command = Chr(34) & path & Chr(34) & " " & inputFilePath & " " & outputFilePath
    ' ?用命令行工具
    shell.Run command
    'shell.Run path & " " & TempFile & " " & outputFilePath
    TempWB.Close savechanges:=False
End Sub




import json, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / 'lime-whisper-theme'
BASE.mkdir(exist_ok=False)
for d in ['themes','assets','scripts','store-assets']:
    (BASE/d).mkdir()
def save(path, obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
manifest = {'name':'lime-whisper-theme','displayName':'Lime Whisper Theme','description':'A gentle citrus-inspired theme with soft lime and mint tones.','version':'1.0.0','publisher':'lilinhuang','engines':{'vscode':'^1.80.0'},'categories':['Themes'],'keywords':['theme','light','dark','lime','mint','pastel'],'icon':'assets/icon.png','license':'MIT','galleryBanner':{'color':'#222B24','theme':'dark'},'contributes':{'themes':[{'label':f'Lime Whisper Theme {v.title()}','uiTheme':'vs' if v=='light' else 'vs-dark','path':f'./themes/lime-whisper-{v}-color-theme.json'} for v in ['light','dark']]}}
save(BASE/'package.json',manifest)
# Each row defines VS Code color IDs followed by the light and dark values.
rows = '''
foreground editor.foreground terminal.foreground input.foreground dropdown.foreground quickInput.foreground editorWidget.foreground editorHoverWidget.foreground editorSuggestWidget.foreground notifications.foreground|354335|DCE6D3
descriptionForeground input.placeholderForeground|7B8872|899B7F
focusBorder inputOption.activeBorder input.border dropdown.border|729B4C|A8D580
editor.background tab.activeBackground|FAFCF5|222B24
titleBar.activeBackground|EDF3E7|1A211B
titleBar.activeForeground|374938|C7D4BC
titleBar.inactiveBackground|F3F5EE|181D19
titleBar.inactiveForeground|788574|798674
activityBar.background|E5EDDC|171E18
activityBar.foreground activityBar.activeBorder|426B36|D7FEB9
activityBar.inactiveForeground|788570|7E9176
sideBar.background|F0F5E9|1C251E
sideBar.foreground|42523D|BCCDB1
sideBarSectionHeader.background|E7EEDC|222D22
sideBarSectionHeader.foreground|4B6041|D1DFC5
panel.background terminal.background|F4F8ED|1E2720
panel.border editorGroup.border tab.border sideBar.border titleBar.border|D8E2CD|354231
statusBar.background statusBar.noFolderBackground|E2EDCF|2A3927
statusBar.foreground statusBar.noFolderForeground|405337|D7E8C6
statusBarItem.hoverBackground|D5E4BC|3A4D32
statusBar.debuggingBackground|D7FEB9|3A5130
statusBar.debuggingForeground|30482C|EAFDB4
editorGroupHeader.tabsBackground tab.inactiveBackground|EAF0E2|19211B
tab.activeForeground|354B30|EAFDB4
tab.activeBorderTop|8AAE58|D7FEB9
tab.inactiveForeground|73816B|91A186
tab.hoverBackground|EAFDB4|2B3929
tab.activeModifiedBorder tab.inactiveModifiedBorder|8A7435|FDFAB0
list.hoverBackground|EAF0DF|293528
list.activeSelectionBackground editorSuggestWidget.selectedBackground|D7FEB9|3A5130
list.activeSelectionForeground list.inactiveSelectionForeground editorSuggestWidget.selectedForeground|30482C|EAFDB4
list.inactiveSelectionBackground|E3ECD5|2E3C2A
list.highlightForeground list.focusHighlightForeground|38796A|A3E3CD
tree.indentGuidesStroke|D3DFC6|354331
editorLineNumber.foreground|94A18B|657660
editorLineNumber.activeForeground|58743F|D7FEB9
editor.lineHighlightBackground|F5F7DF|2B3628
editor.lineHighlightBorder|E9EDCC|34422E
editorCursor.foreground|527D38|EAFDB4
selection.background editor.selectionBackground terminal.selectionBackground|D2EBC2|456039
editor.inactiveSelectionBackground|E1E9D7|35472F
editor.wordHighlightBackground editor.wordHighlightStrongBackground editor.selectionHighlightBackground|EAF1D580|34482F99
editor.findMatchHighlightBackground|FDFAB0|635D2B
editor.findMatchBackground|EDD978|887B36
editor.findMatchBorder|A18B36|FDFAB0
editorBracketMatch.background|EAFDB4|3B5130
editorBracketMatch.border|8DAA61|A7CD7D
editorIndentGuide.background1|E0E7D6|344232
editorIndentGuide.activeBackground1|A2B784|6D8757
editorWhitespace.foreground|CCD5C1|455541
editorRuler.foreground|DEE6D3|354431
textLink.foreground textLink.activeForeground editorLink.activeForeground|38796A|A3E3CD
quickInput.background editorHoverWidget.background notifications.background|F8FBF0|283329
input.background dropdown.background|FCFDF8|1D271F
editorWidget.background editorSuggestWidget.background|F4F8EB|283329
editorWidget.border editorHoverWidget.border editorSuggestWidget.border notifications.border|CFDCBF|45583B
button.background|D7FEB9|D7FEB9
button.foreground button.hoverForeground|30482C|263820
button.hoverBackground|C6EEA5|EAFDB4
button.secondaryBackground|E8EFDE|3A4B32
button.secondaryForeground|4B6041|DCE6D3
button.secondaryHoverBackground|DCE8CC|4B603F
badge.background activityBarBadge.background|66864A|D7FEB9
badge.foreground activityBarBadge.foreground|FFFFFF|263820
scrollbarSlider.background|9BAE8055|9FB88A44
scrollbarSlider.hoverBackground scrollbarSlider.activeBackground|829C6977|B7D59D66
errorForeground editorError.foreground problemsErrorIcon.foreground gitDecoration.deletedResourceForeground editorGutter.deletedBackground|B65353|E99B91
editorWarning.foreground problemsWarningIcon.foreground|947223|E5CD83
editorInfo.foreground problemsInfoIcon.foreground|39796D|A3E3CD
gitDecoration.addedResourceForeground gitDecoration.untrackedResourceForeground editorGutter.addedBackground|5E934B|ACDB8D
gitDecoration.modifiedResourceForeground editorGutter.modifiedBackground|A18B3C|E4D58E
diffEditor.insertedTextBackground|E5F3DC99|2B402B99
diffEditor.removedTextBackground|F7E7E299|422D2B99
diffEditor.insertedLineBackground|E5F3DC66|2B402B66
diffEditor.removedLineBackground|F7E7E266|422D2B66
'''
tokens=[('comment','7D8872','819479','italic'),('keyword,storage','657A2E','EAFDB4',''),('string','39764A','C6FEBE',''),('entity.name.function,support.function','28796E','A3E3CD',''),('entity.name.type,support.type,support.class','697B28','D7FEB9',''),('constant.numeric,constant.language,variable.other.constant','8B682D','FDFAB0',''),('variable','354335','DCE6D3',''),('variable.parameter','626E45','D4DDB5',''),('variable.other.property,support.variable.property','486C59','C3FFCD',''),('keyword.operator','657359','BBCDA7',''),('punctuation','7E8B73','91A68A',''),('entity.name.tag','527536','D7FEB9',''),('entity.other.attribute-name','8B7438','E5D99C',''),('string.regexp','78628A','CFB8DB',''),('constant.character.escape','9A6D3D','E9C391',''),('markup.heading','527536','D7FEB9','bold'),('markup.bold','354335','DCE6D3','bold'),('markup.italic','354335','DCE6D3','italic'),('invalid','B65353','E99B91','')]
ansiL=['354335','B65353','527D38','947223','547D91','886A96','39796D','788570','85917A','C3645C','638E43','A4862D','6492A7','9B7AA8','4B9280','263820']
ansiD=['354232','E99B91','BDE8A0','E5D99C','A3CADB','CFB8DB','A3E3CD','DCE6D3','819479','F2B0A7','D7FEB9','FDFAB0','B9DEEB','DFC9E8','C3FFCD','F3F9EA']
ansiNames=['Black','Red','Green','Yellow','Blue','Magenta','Cyan','White']
for idx,variant in enumerate(['light','dark']):
    colors={}
    for row in rows.strip().splitlines():
        ids,l,d=row.split('|')
        for key in ids.split(): colors[key]='#'+[l,d][idx]
    colors.pop('button.hoverForeground',None)
    for i,c in enumerate([ansiL,ansiD][idx]): colors['terminal.ansi'+('Bright' if i>=8 else '')+ansiNames[i%8]]='#'+c
    rules=[{'scope':scope.split(','),'settings':{'foreground':'#'+[l,d][idx],**({'fontStyle':style} if style else {})}} for scope,l,d,style in tokens]
    semantic={'variable':'#'+['354335','DCE6D3'][idx],'parameter':'#'+['626E45','D4DDB5'][idx],'property':'#'+['486C59','C3FFCD'][idx],'function':'#'+['28796E','A3E3CD'][idx],'method':'#'+['28796E','A3E3CD'][idx],'type':'#'+['697B28','D7FEB9'][idx],'class':'#'+['697B28','D7FEB9'][idx],'interface':'#'+['697B28','D7FEB9'][idx],'variable.readonly':'#'+['8B682D','FDFAB0'][idx]}
    save(BASE/'themes'/f'lime-whisper-{variant}-color-theme.json',{'name':f'Lime Whisper Theme {variant.title()}','type':variant,'colors':colors,'semanticHighlighting':True,'semanticTokenColors':semantic,'tokenColors':rules})
shutil.copy(ROOT/'moss-lantern-theme/LICENSE',BASE/'LICENSE')
(BASE/'.vscodeignore').write_text('scripts/**\n.tmp/**\n**/__pycache__/**\n*.vsix\nassets/logo-original.png\nassets/logo-prompt.txt\n',encoding='utf-8')
(BASE/'CHANGELOG.md').write_text('# Changelog\n\n## 1.0.0\n\n- Initial release with coordinated Light and Dark themes.\n',encoding='utf-8')
shutil.copytree(ROOT/'moss-lantern-theme/scripts/demo-project',BASE/'scripts/demo-project')
capture=(ROOT/'moss-lantern-theme/scripts/capture-real-screenshots.py').read_text(encoding='utf-8').replace('Moss Lantern','Lime Whisper').replace('moss-lantern','lime-whisper')
(BASE/'scripts/capture-real-screenshots.py').write_text(capture,encoding='utf-8')
for p in (BASE/'scripts/demo-project').rglob('*'):
    if p.is_file() and p.suffix in ['.js','.json','.md','.css','.html']:
        p.write_text(p.read_text(encoding='utf-8').replace('Moss Lantern','Lime Whisper').replace('moss-lantern','lime-whisper'),encoding='utf-8')
(BASE/'README.md').write_text('''# Lime Whisper Theme

A gentle citrus-inspired theme with soft lime and mint tones.

![Lime Whisper logo](assets/icon.png)

## Two coordinated appearances

- **Lime Whisper Theme Light** — creamy white editor, gentle green panels, deep botanical text.
- **Lime Whisper Theme Dark** — charcoal green editor, lime keywords and mint strings.

### Light

![Light preview](store-assets/screenshots/en/screenshot-light.png)

### Dark

![Dark preview](store-assets/screenshots/en/screenshot-dark.png)

## Install

Install the VSIX using **Extensions: Install from VSIX**, then select either variant with **Preferences: Color Theme**.

Includes semantic highlighting, terminal colors, Git decorations and readable search/selection states.

Publisher: **lilinhuang** · Version: **1.0.0**

[Marketplace](https://marketplace.visualstudio.com/items?itemName=lilinhuang.lime-whisper-theme)
''',encoding='utf-8')
print('Created',BASE)

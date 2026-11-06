# v1.1 (run when the Game Center app update ships): privacy and terms describe the optional Game Center leaderboard.
P='privacy.html'; T='terms.html'
p=open(P,encoding='utf-8').read(); t=open(T,encoding='utf-8').read()
PE=[
("<p>The Wienerboard shows your own top 5 runs. It is stored only on the device you play on; there is no online leaderboard, no player names, and nothing you type is shared with other players.",
 "<p>The Wienerboard shows your own top 5 runs. It is stored only on the device you play on; nothing you type is shared with other players."),
("Clearing your browser's site data or deleting the App erases it.</p>\n  <h2>4. Service Providers</h2>",
 "Clearing your browser's site data or deleting the App erases it.</p>\n  <p><strong>Game Center (App only, optional):</strong> if you choose to use Apple Game Center by tapping the App's Game Center button, the App sends your final score and any achievements you unlock to Game Center, where they appear on Apple's global Franks and Buns High Scores leaderboard under your Game Center nickname. Apple runs Game Center under its own privacy policy; we do not receive your Apple ID, name, or contact details. You can sign out of Game Center or change who sees your activity in your iPhone or iPad Settings.</p>\n  <h2>4. Service Providers</h2>"),
("advertising on the Site only. See <a href=\"https://policies.google.com/technologies/partner-sites\" target=\"_blank\" rel=\"noopener\">how Google uses data when you use our partners' sites or apps</a>.</li>\n  </ul>",
 "advertising on the Site only. See <a href=\"https://policies.google.com/technologies/partner-sites\" target=\"_blank\" rel=\"noopener\">how Google uses data when you use our partners' sites or apps</a>.</li>\n    <li><strong>Apple Game Center</strong> (Apple Inc.) — optional scores, leaderboard and achievements in the App. <a href=\"https://www.apple.com/legal/privacy/\" target=\"_blank\" rel=\"noopener\">Apple Privacy Policy</a></li>\n  </ul>"),
]
TE=[
("Scores can be lost if you clear your browser's site data or delete the App, and we cannot restore them.</p>",
 "Scores can be lost if you clear your browser's site data or delete the App, and we cannot restore them. In the App, if you use Apple Game Center, your final scores and achievements are also posted to Apple's Franks and Buns High Scores leaderboard under your Game Center nickname; Game Center is provided by Apple under Apple's terms.</p>"),
]
if 'Apple Game Center' in p: print('already applied'); raise SystemExit
for s,E,n in ((p,PE,P),(t,TE,T)):
    for o,_ in E:
        if s.count(o)!=1: raise SystemExit('anchor not found exactly once in '+n+', nothing written: '+o[:60])
PE.append(('Last updated: October 29, 2026','Last updated: November 5, 2026'))
TE.append(('Last updated: October 29, 2026','Last updated: November 5, 2026'))
for o,n in PE: p=p.replace(o,n,1)
for o,n in TE: t=t.replace(o,n,1)
open(P,'w',encoding='utf-8').write(p); open(T,'w',encoding='utf-8').write(t); print('privacy and terms updated for Game Center')

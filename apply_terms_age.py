# Terms/privacy: match the 4+ App Store rating, drop the "addictive" wording, tighten liability. Run from the repo folder.
T='terms.html'; P='privacy.html'
t=open(T,encoding='utf-8').read(); p=open(P,encoding='utf-8').read()
TE=[
('<p class="updated">Last updated: October 15, 2026</p>', '<p class="updated">Last updated: October 29, 2026</p>'),
('<p>By using this Site, you confirm that you are at least 13 years of age, or that you have the consent of a parent or guardian. This Site is not directed at children under the age of 13. If you are under 13, please do not use this Site.</p>',
 '<p>Franks &amp; Buns is a general-audience game. The App is rated 4+ on the App Store, which describes its content; it does not mean the game is designed for children. If you are under 18 (or the age of majority where you live), you may use the Site and App only with the involvement of a parent or guardian, who agrees to these Terms on your behalf and is responsible for your use, including how long you play. The website shows third-party advertising and is not directed at children under 13.</p>'),
('<li>Franks &amp; Buns and its operators are not responsible for any physical, emotional, or psychological effects arising from your use of the game.</li>',
 '<li>To the fullest extent permitted by law, SLAE Labs LLC is not responsible for any physical, emotional, or psychological effects arising from your use of the game.</li>'),
('<p>We designed Franks &amp; Buns to be addictive and fun — that\'s the point of a great arcade game. However, we strongly encourage all players to:</p>',
 '<p>Franks &amp; Buns is meant to be quick, lighthearted fun. We encourage all players to:</p>'),
('<p>If you or someone you know is struggling with compulsive gaming, resources are available at <a href="https://www.ncpgambling.org" target="_blank" rel="noopener">ncpgambling.org</a> and similar organisations.</p>',
 '<p>If you or someone you know finds it hard to control time spent gaming, consider talking to a doctor or another qualified professional.</p>'),
('arising from your use of or inability to use the Site.</p>',
 'arising from your use of or inability to use the Site.</p>\n  <p>To the fullest extent permitted by law, our total liability for any claim relating to the Site or App is limited to fifty U.S. dollars (US$50). Some jurisdictions do not allow certain warranties to be excluded or liability to be limited, so some of the above may not apply to you; in that case our liability is limited to the smallest amount the law allows.</p>\n  <p>You agree to indemnify and hold harmless SLAE Labs LLC from any claims, losses, or expenses (including reasonable legal fees) arising from your misuse of the Site or App or your breach of these Terms.</p>'),
('without regard to its conflict of law provisions.</p>',
 'without regard to its conflict of law provisions. If any part of these Terms is found unenforceable, the rest remains in effect.</p>'),
]
PE=[
('<p>Franks &amp; Buns is a general-audience game and is not directed at children under 13. We do not knowingly collect personal information from children under 13. The game never asks for a name, email address, or contact details.</p>',
 '<p>Franks &amp; Buns is a general-audience game and is not directed at children under 13. The App is rated 4+ on the App Store, which describes its content, not its intended audience. We do not knowingly collect personal information from children under 13. The game never asks for a name, email address, or contact details. If you believe a child under 13 has sent us personal information, contact us at admin@slaelabs.com and we will delete it.</p>'),
]
if 'rated 4+ on the App Store' in t: print('already applied'); raise SystemExit
for s,E,name in ((t,TE,T),(p,PE,P)):
    for o,n in E:
        if s.count(o)!=1: raise SystemExit('anchor not found exactly once in '+name+', nothing written: '+o[:70])
for o,n in TE: t=t.replace(o,n,1)
for o,n in PE: p=p.replace(o,n,1)
open(T,'w',encoding='utf-8').write(t); open(P,'w',encoding='utf-8').write(p); print('terms and privacy updated')

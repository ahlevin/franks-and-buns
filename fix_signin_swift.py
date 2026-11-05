# Game Center: never show Apple's sign-in sheet on its own. Signed-in players connect silently;
# everyone else sees it only after tapping the Game Center button.
import sys
OLD_START = "    // Sign the player in. If they're not signed in to Game Center"
OLD_END = "    @objc func submitScore(_ call: CAPPluginCall) {"
NEW = '''    // Sign-in never interrupts the game. Players already signed in to Game Center on their iPhone are
    // connected silently (iOS may show its small "Welcome back" banner). For anyone else, Apple's sign-in
    // sheet is kept and shown ONLY when the player taps the Game Center button (call with present: true).
    private var pendingSignInVC: UIViewController?
    private var handlerInstalled = false
    private var waitingCall: CAPPluginCall?

    @objc func signIn(_ call: CAPPluginCall) {
        let present = call.getBool("present") ?? false
        DispatchQueue.main.async {
            let player = GKLocalPlayer.local
            if player.isAuthenticated { call.resolve(["signedIn": true]); return }
            if present {
                guard let vc = self.pendingSignInVC else { call.resolve(["signedIn": false]); return }
                self.pendingSignInVC = nil
                self.waitingCall = call
                self.bridge?.viewController?.present(vc, animated: true)
                return
            }
            if self.handlerInstalled { call.resolve(["signedIn": false]); return }
            self.handlerInstalled = true
            var answered = false
            player.authenticateHandler = { [weak self] signInVC, _ in
                guard let self = self else { return }
                if let vc = signInVC {
                    self.pendingSignInVC = vc   // not shown automatically
                    if !answered { answered = true; call.resolve(["signedIn": false]) }
                    return
                }
                if !answered { answered = true; call.resolve(["signedIn": player.isAuthenticated]) }
                if let waiting = self.waitingCall { self.waitingCall = nil; waiting.resolve(["signedIn": player.isAuthenticated]) }
            }
        }
    }

'''
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    if 'pendingSignInVC' in s: print(p, 'already applied'); continue
    a = s.find(OLD_START); b = s.find(OLD_END)
    if a < 0 or b < 0 or s.count(OLD_START) != 1: raise SystemExit('anchor not found in ' + p + ', nothing written')
    s = s[:a] + NEW + s[b:]
    open(p, 'w', encoding='utf-8').write(s); print(p, 'sign-in made opt-in')

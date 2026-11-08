import os
import base64
import re

def get_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/webp;base64,' + base64.b64encode(f.read()).decode('utf-8')

b64_cap = get_b64('imgs/bottlee_top.webp')
b64_f1 = get_b64('imgs/juggernaut_frame1.webp')
b64_f2 = get_b64('imgs/juggernaut_frame2.webp')
b64_f3 = get_b64('imgs/juggernaut_frame3.webp')

print("Loaded WebP images:")
print(f"Cap: {len(b64_cap)} chars")
print(f"F1: {len(b64_f1)} chars")
print(f"F2: {len(b64_f2)} chars")
print(f"F3: {len(b64_f3)} chars")

with open('code.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. UPDATE ASSET_B64 & IMAGE_ASSETS
old_asset_pattern = r'const ASSET_B64 = \{[\s\S]*?IMAGE_ASSETS\.juggernaut_machine\.src = ASSET_B64\.juggernaut_machine;(?:\s*IMAGE_ASSETS\.bottlee_top\.src = ASSET_B64\.bottlee_top;\s*IMAGE_ASSETS\.juggernaut_bottle_f1\.src = ASSET_B64\.juggernaut_bottle_f1;\s*IMAGE_ASSETS\.juggernaut_bottle_f2\.src = ASSET_B64\.juggernaut_bottle_f2;\s*IMAGE_ASSETS\.juggernaut_bottle_f3\.src = ASSET_B64\.juggernaut_bottle_f3;)?'

match = re.search(old_asset_pattern, content)
if match:
    old_asset_block = match.group(0)
    m_perk = re.search(r'juggernaut_perk:\s*"([^"]+)"', old_asset_block)
    m_can = re.search(r'juggernaut_can:\s*"([^"]+)"', old_asset_block)
    m_mach = re.search(r'juggernaut_machine:\s*"([^"]+)"', old_asset_block)

    b64_perk = m_perk.group(1) if m_perk else ""
    b64_can = m_can.group(1) if m_can else ""
    b64_mach = m_mach.group(1) if m_mach else ""

    new_asset_block = f'''const ASSET_B64 = {{
        juggernaut_perk: "{b64_perk}",
        juggernaut_can: "{b64_can}",
        juggernaut_machine: "{b64_mach}",
        bottlee_top: "{b64_cap}",
        juggernaut_bottle_f1: "{b64_f1}",
        juggernaut_bottle_f2: "{b64_f2}",
        juggernaut_bottle_f3: "{b64_f3}"
    }};

    const IMAGE_ASSETS = {{
        juggernaut_perk: new Image(),
        juggernaut_can: new Image(),
        juggernaut_machine: new Image(),
        bottlee_top: new Image(),
        juggernaut_bottle_f1: new Image(),
        juggernaut_bottle_f2: new Image(),
        juggernaut_bottle_f3: new Image()
    }};

    IMAGE_ASSETS.juggernaut_perk.src = ASSET_B64.juggernaut_perk;
    IMAGE_ASSETS.juggernaut_can.src = ASSET_B64.juggernaut_can;
    IMAGE_ASSETS.juggernaut_machine.src = ASSET_B64.juggernaut_machine;
    IMAGE_ASSETS.bottlee_top.src = ASSET_B64.bottlee_top;
    IMAGE_ASSETS.juggernaut_bottle_f1.src = ASSET_B64.juggernaut_bottle_f1;
    IMAGE_ASSETS.juggernaut_bottle_f2.src = ASSET_B64.juggernaut_bottle_f2;
    IMAGE_ASSETS.juggernaut_bottle_f3.src = ASSET_B64.juggernaut_bottle_f3;'''

    content = content.replace(old_asset_block, new_asset_block)
    print("Updated ASSET_B64 successfully!")

# 2. SOUND HELPERS
old_sounds_pattern = r'function playBottleCapPopSound\(\) \{[\s\S]*?function playPerkActivateSound\(\) \{[\s\S]*?\} catch\(e\) \{\}\s*\}|function playCanOpenSound\(\) \{[\s\S]*?function playPerkActivateSound\(\) \{[\s\S]*?\} catch\(e\) \{\}\s*\}'
m_sounds = re.search(old_sounds_pattern, content)
if m_sounds:
    new_sounds = '''function playBottleCapPopSound() {
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {
            // Clique metálico estridente da tampa sendo sacada
            if (toneSynth) {
                toneSynth.triggerAttackRelease(["E5", "G#5", "B5", "E6"], "64n");
                setTimeout(() => {
                    try { if (toneSynth) toneSynth.triggerAttackRelease(["G6", "B6"], "64n"); } catch(e){}
                }, 40);
            }
            // Hiss / spray de gás pressurizado da garrafa (PSSSST!)
            if (audioCtx) {
                let bufferSize = Math.floor(audioCtx.sampleRate * 0.45);
                let buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                let data = buffer.getChannelData(0);
                for (let i = 0; i < bufferSize; i++) {
                    let decay = Math.exp(-i / (audioCtx.sampleRate * 0.08));
                    data[i] = (Math.random() * 2 - 1) * decay;
                }
                let noise = audioCtx.createBufferSource();
                noise.buffer = buffer;
                let filter = audioCtx.createBiquadFilter();
                filter.type = 'highpass';
                filter.frequency.value = 3500;
                let gain = audioCtx.createGain();
                gain.gain.value = 0.85 * audioSettings.sfxVolume;
                noise.connect(filter);
                filter.connect(gain);
                gain.connect(audioCtx.destination);
                noise.start();
            }
        } catch(e) {}
    }

    function playBottleThrowSound() {
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {
            // Whoosh do braço robótico jogando a garrafa
            if (audioCtx) {
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(420, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(110, audioCtx.currentTime + 0.28);
                gain.gain.setValueAtTime(0.55 * audioSettings.sfxVolume, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.28);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.29);
            }
            // Som do vidro da garrafa quebrando/quicando ao longe
            setTimeout(() => {
                try {
                    if (toneSynth) {
                        toneSynth.triggerAttackRelease(["C6", "F#6", "A#6"], "64n");
                        setTimeout(() => {
                            try { if (toneSynth) toneSynth.triggerAttackRelease(["D6", "G6"], "64n"); } catch(e){}
                        }, 70);
                    }
                } catch(e) {}
            }, 380);
        } catch(e) {}
    }

    function playCanOpenSound() {
        playBottleCapPopSound();
    }

    function playCanDrinkSound() {
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {
            if (toneSynth) {
                toneSynth.triggerAttackRelease("C3", "32n");
                setTimeout(() => {
                    try { if (toneSynth) toneSynth.triggerAttackRelease("D3", "32n"); } catch(e){}
                }, 170);
                setTimeout(() => {
                    try { if (toneSynth) toneSynth.triggerAttackRelease("E3", "32n"); } catch(e){}
                }, 340);
            }
        } catch(e) {}
    }

    function playPerkActivateSound() {
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {
            if (toneSynth) {
                toneSynth.triggerAttackRelease(["C4", "G4", "C5", "E5"], "8n");
            }
            if (toneLowSynth) {
                toneLowSynth.triggerAttackRelease("C2", "8n");
            }
        } catch(e) {}
    }'''
    content = content.replace(m_sounds.group(0), new_sounds)
    print("Updated sound helpers successfully!")

# 3. startPerkDrinking
old_start_pattern = r'function startPerkDrinking\(perkType\) \{[\s\S]*?playGenericSound\(\'buy\'\);\s*\}'
new_start_drinking = '''function startPerkDrinking(perkType) {
        player.isDrinkingPerk = true;
        player.perkDrinkTimer = 0;
        player.perkDrinkDuration = 3.0;
        player.perkDrinkType = perkType;
        player.canTabPopped = false;
        player.canDrinkGulpPlayed = false;
        player.perkActivated = false;
        player.bottleThrownPlayed = false;
        perkDrinkFizzParticles = [];
        playGenericSound('buy');
    }'''
content = re.sub(old_start_pattern, lambda m: new_start_drinking, content)

# 4. PLAYER DRINKING TIMELINE
old_drink_loop_pattern = r'// Atualização da animação e efeitos de beber Perk(?: Garrafa)? \(Juggernaut\)\s*if \(player\.isDrinkingPerk\) \{[\s\S]*?if \(t >= player\.perkDrinkDuration\) \{[\s\S]*?\}\s*\}'
new_player_drink_loop = '''// Atualização da animação e efeitos de beber Perk Garrafa (Juggernaut)
        if (player.isDrinkingPerk) {
            player.perkDrinkTimer += dt;
            let t = player.perkDrinkTimer;

            // Frame 2: t = 1.05s: Mão esquerda saca a tampa (Bottlee Top voa + som de abertura e gás)
            if (t >= 1.05 && !player.canTabPopped) {
                player.canTabPopped = true;
                playBottleCapPopSound();
                spawnCanFizzParticles();
            }

            // Frame 3: t = 1.50s: Inclinando a garrafa e bebendo (goles refrescantes)
            if (t >= 1.50 && !player.canDrinkGulpPlayed) {
                player.canDrinkGulpPlayed = true;
                playCanDrinkSound();
            }

            // t = 2.05s: Ativação oficial do Juggernaut (+100 de Vida)
            if (t >= 2.05 && !player.perkActivated) {
                player.perkActivated = true;
                player.perks['JUGGERNAUT'] = true;
                player.maxHealth = 200;
                player.health = Math.min(200, player.health + 100);
                player.juggernautJustAcquiredTimer = 3.5;
                screenFlash = 0.9;
                screenShake = 0.35;
                playPerkActivateSound();
                damageTexts.push(new DamageText(player.x, player.y - 45, '★ JUGGERNAUT ATIVADO! (+100 VIDA) ★', '#ef4444', 2.5));
            }

            // Frame 3 -> Final: t = 2.35s: Joga a garrafa fora (arremesso para longe)
            if (t >= 2.35 && !player.bottleThrownPlayed) {
                player.bottleThrownPlayed = true;
                playBottleThrowSound();
            }

            if (t >= player.perkDrinkDuration) {
                player.isDrinkingPerk = false;
                player.perkDrinkTimer = 0;
                player.bottleThrownPlayed = false;
            }
        }'''
content = re.sub(old_drink_loop_pattern, lambda m: new_player_drink_loop, content)

# 5. OVERLAY
old_overlay_pattern = r'(?:// ================= DESENHO PROCEDURAL DE BRAÇOS, MÃOS E DEDOS DO ROBÔ =================[\s\S]*?)?// ================= ANIMAÇÃO DE ABERTURA E BEBIDA DA (?:LATA|GARRAFA) JUGGERNAUT \(1ª PESSOA\) =================[\s\S]*?function drawPerkDrinkingOverlay\(ctx\) \{[\s\S]*?\n    \}\n'
m_ov = re.search(old_overlay_pattern, content)
if m_ov:
    new_overlay_code = '''// ================= DESENHO PROCEDURAL DE BRAÇOS, MÃOS E DEDOS DO ROBÔ =================
    // Placas de blindagem mecânica, juntas articuladas e contorno na cor personalizada do jogador
    function drawRobotForearm(ctx, startX, startY, endX, endY, width, customColor) {
        ctx.save();
        let dx = endX - startX;
        let dy = endY - startY;
        let angle = Math.atan2(dy, dx);
        let len = Math.hypot(dx, dy);

        ctx.translate(startX, startY);
        ctx.rotate(angle);

        let halfW = width * 0.5;

        // 1. Placa principal de liga de titânio (cinza chumbo / carbono)
        let armGrad = ctx.createLinearGradient(0, -halfW, 0, halfW);
        armGrad.addColorStop(0, '#334155');
        armGrad.addColorStop(0.3, '#1e293b');
        armGrad.addColorStop(0.7, '#0f172a');
        armGrad.addColorStop(1, '#1e293b');

        ctx.fillStyle = armGrad;
        ctx.beginPath();
        ctx.moveTo(0, -halfW * 1.35);
        ctx.lineTo(len * 0.65, -halfW);
        ctx.lineTo(len, -halfW * 0.75);
        ctx.lineTo(len, halfW * 0.75);
        ctx.lineTo(len * 0.65, halfW);
        ctx.lineTo(0, halfW * 1.35);
        ctx.closePath();
        ctx.fill();

        // 2. Contorno neon na cor do personagem
        ctx.strokeStyle = customColor;
        ctx.lineWidth = 2.4;
        ctx.shadowColor = customColor;
        ctx.shadowBlur = 8;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // 3. Pistão hidráulico / canaleta interna de energia
        ctx.fillStyle = '#475569';
        ctx.fillRect(len * 0.15, -3, len * 0.55, 6);
        ctx.fillStyle = customColor;
        ctx.shadowColor = customColor;
        ctx.shadowBlur = 6;
        ctx.fillRect(len * 0.22, -1.2, len * 0.42, 2.4);
        ctx.shadowBlur = 0;

        // 4. Conector / servo de punho rotativo
        let cuffGrad = ctx.createLinearGradient(len - 14, 0, len, 0);
        cuffGrad.addColorStop(0, '#1e293b');
        cuffGrad.addColorStop(0.5, '#475569');
        cuffGrad.addColorStop(1, '#0f172a');
        ctx.fillStyle = cuffGrad;
        ctx.fillRect(len - 14, -halfW * 0.85, 14, halfW * 1.7);
        ctx.strokeStyle = customColor;
        ctx.lineWidth = 2.0;
        ctx.strokeRect(len - 14, -halfW * 0.85, 14, halfW * 1.7);

        // Rebites metálicos da junta do punho
        ctx.fillStyle = '#e2e8f0';
        ctx.beginPath();
        ctx.arc(len - 7, -halfW * 0.45, 2, 0, Math.PI * 2);
        ctx.arc(len - 7, halfW * 0.45, 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }

    function drawRobotPalmChassis(ctx, palmX, palmY, angle, size, customColor) {
        ctx.save();
        ctx.translate(palmX, palmY);
        ctx.rotate(angle);

        // Chassis da palma da mão mecânica com chanfros
        let palmGrad = ctx.createRadialGradient(-3, -3, 2, 0, 0, size * 0.7);
        palmGrad.addColorStop(0, '#475569');
        palmGrad.addColorStop(0.6, '#1e293b');
        palmGrad.addColorStop(1, '#0f172a');

        ctx.fillStyle = palmGrad;
        ctx.beginPath();
        ctx.moveTo(-size * 0.5, -size * 0.6);
        ctx.lineTo(size * 0.5, -size * 0.5);
        ctx.lineTo(size * 0.65, size * 0.5);
        ctx.lineTo(-size * 0.5, size * 0.6);
        ctx.closePath();
        ctx.fill();

        ctx.strokeStyle = customColor;
        ctx.lineWidth = 2.2;
        ctx.shadowColor = customColor;
        ctx.shadowBlur = 7;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Barra de nós dos dedos (knuckles metálicos com rebites)
        for (let k = -2; k <= 2; k++) {
            let kx = size * 0.48;
            let ky = k * (size * 0.22);
            ctx.fillStyle = '#64748b';
            ctx.beginPath();
            ctx.arc(kx, ky, 3.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 1.2;
            ctx.stroke();
            ctx.fillStyle = '#f8fafc';
            ctx.beginPath();
            ctx.arc(kx, ky, 1.2, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }

    // Dedos articulados de robô envolvendo e segurando a garrafa
    function drawRobotGrippingFingers(ctx, palmX, palmY, bottleX, bottleY, bottleW, customColor, isRight) {
        ctx.save();
        let fingerSpacing = 20;
        let startFingerY = bottleY + 12;

        for (let f = 0; f < 4; f++) {
            let fy = startFingerY + f * fingerSpacing;
            let fx = isRight ? (bottleX + bottleW * 0.35) : (bottleX - bottleW * 0.35);
            let dir = isRight ? -1 : 1; // Dedos apontam para o centro da garrafa
            let segLen1 = 22;
            let segLen2 = 18;
            let segLen3 = 14;

            ctx.save();
            ctx.translate(fx, fy);

            // Falange Proximal
            ctx.fillStyle = '#1e293b';
            ctx.beginPath();
            ctx.roundRect(0, -6, dir * segLen1, 12, 3);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 2.0;
            ctx.shadowColor = customColor;
            ctx.shadowBlur = 6;
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Haste / Pino da junta
            ctx.fillStyle = '#e2e8f0';
            ctx.beginPath();
            ctx.arc(dir * segLen1, 0, 2.8, 0, Math.PI * 2);
            ctx.fill();

            // Falange Intermediária (curvando sobre a garrafa)
            ctx.translate(dir * segLen1, 0);
            ctx.rotate(dir * 0.35);
            ctx.fillStyle = '#334155';
            ctx.beginPath();
            ctx.roundRect(0, -5, dir * segLen2, 10, 3);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 1.8;
            ctx.stroke();

            // Falange Distal / Ponta do dedo de robô (almofada de aderência de silicone)
            ctx.translate(dir * segLen2, 0);
            ctx.rotate(dir * 0.45);
            ctx.fillStyle = '#0f172a';
            ctx.beginPath();
            ctx.roundRect(0, -4.5, dir * segLen3, 9, 3);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 1.8;
            ctx.stroke();

            // Gripper pad interno escuro
            ctx.fillStyle = '#020617';
            ctx.fillRect(dir * 2, -2, dir * (segLen3 - 4), 4);

            ctx.restore();
        }

        // Polegar mecânico na lateral
        let thumbY = startFingerY - 26;
        let thumbX = isRight ? (bottleX + bottleW * 0.42) : (bottleX - bottleW * 0.42);
        ctx.save();
        ctx.translate(thumbX, thumbY);
        let tDir = isRight ? -1 : 1;
        ctx.rotate(tDir * 0.7);
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.roundRect(0, -7, tDir * 28, 14, 4);
        ctx.fill();
        ctx.strokeStyle = customColor;
        ctx.lineWidth = 2.0;
        ctx.stroke();

        ctx.fillStyle = '#e2e8f0';
        ctx.beginPath();
        ctx.arc(tDir * 28, 0, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        ctx.restore();
    }

    // Mão esquerda de robô retirando a tampa
    function drawRobotLeftHandRemovingCap(ctx, capX, capY, progress, customColor) {
        ctx.save();
        let gripX = capX - 18 + progress * 24;
        let gripY = capY - 14 - progress * 40;

        ctx.save();
        ctx.translate(gripX, gripY);
        ctx.rotate(-0.45 + progress * 0.8);

        // Palma esquerda do robô
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.roundRect(-20, -14, 40, 28, 5);
        ctx.fill();
        ctx.strokeStyle = customColor;
        ctx.lineWidth = 2.2;
        ctx.shadowColor = customColor;
        ctx.shadowBlur = 6;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Dedos de pinça mecânica sacando a tampa
        for (let d = -1; d <= 1; d++) {
            ctx.fillStyle = '#334155';
            ctx.beginPath();
            ctx.roundRect(14, d * 8 - 4, 18, 8, 3);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 1.8;
            ctx.stroke();
            // Pino
            ctx.fillStyle = '#e2e8f0';
            ctx.beginPath();
            ctx.arc(28, d * 8, 2, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();

        ctx.restore();
    }

    // Mão direita aberta lançando a garrafa
    function drawRobotHandThrowing(ctx, handX, handY, angle, customColor) {
        ctx.save();
        ctx.translate(handX, handY);
        ctx.rotate(angle);

        // Palma mecânica estendida
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.roundRect(-24, -20, 48, 40, 6);
        ctx.fill();
        ctx.strokeStyle = customColor;
        ctx.lineWidth = 2.4;
        ctx.shadowColor = customColor;
        ctx.shadowBlur = 8;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Dedos abertos em leque lançando para frente
        let fingerAngles = [-0.55, -0.25, 0.0, 0.28, 0.6];
        for (let i = 0; i < fingerAngles.length; i++) {
            ctx.save();
            ctx.translate(20, -16 + i * 8);
            ctx.rotate(fingerAngles[i]);

            ctx.fillStyle = '#334155';
            ctx.beginPath();
            ctx.roundRect(0, -4, 26, 8, 3);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 1.8;
            ctx.stroke();

            ctx.fillStyle = '#e2e8f0';
            ctx.beginPath();
            ctx.arc(22, 0, 2, 0, Math.PI * 2);
            ctx.fill();

            // Ponta esticada
            ctx.fillStyle = '#0f172a';
            ctx.beginPath();
            ctx.roundRect(26, -3, 14, 6, 2);
            ctx.fill();
            ctx.strokeStyle = customColor;
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.restore();
        }

        ctx.restore();
    }

    // ================= ANIMAÇÃO DE ABERTURA E BEBIDA DA GARRAFA JUGGERNAUT (1ª PESSOA) =================
    function drawPerkDrinkingOverlay(ctx) {
        if (!player || !player.isDrinkingPerk) return;

        let W = canvas.width;
        let H = canvas.height;
        let timer = player.perkDrinkTimer;
        let dur = player.perkDrinkDuration || 3.0;
        let p = Math.min(1, Math.max(0, timer / dur));

        let cx = W * 0.5;
        let baseY = H;
        let userColor = characterConfig.color || '#38bdf8';

        // Dimensões da garrafa proporcional com base nos sprites transparentes
        let bottleH = Math.min(640, Math.max(440, H * 0.68));
        let bottleW = bottleH * (237 / 756);

        ctx.save();

        // Vinheta atmosférica vermelha de foco no perk
        let vigAlpha = Math.sin(p * Math.PI) * 0.38;
        let vigGrad = ctx.createRadialGradient(W / 2, H / 2, W * 0.22, W / 2, H / 2, W * 0.78);
        vigGrad.addColorStop(0, 'rgba(0,0,0,0)');
        vigGrad.addColorStop(1, `rgba(185, 28, 28, ${vigAlpha})`);
        ctx.fillStyle = vigGrad;
        ctx.fillRect(0, 0, W, H);

        if (p < 0.28) {
            // ================= FASE 1: MOSTRANDO A GARRAFA FECHADA (FRAME 1) =================
            let t1 = p / 0.28;
            let ease = Math.sin(t1 * Math.PI / 2);
            let bY = baseY + (1 - ease) * (bottleH + 90) - bottleH * 0.52;
            let bX = cx + bottleW * 0.12;
            let bRot = -0.04 * ease;

            // Braço direito de robô subindo com a garrafa
            let armRightEndX = bX + bottleW * 0.42;
            let armRightEndY = bY + bottleH * 0.18;
            drawRobotForearm(ctx, cx + W * 0.38, baseY, armRightEndX, armRightEndY, 48, userColor);
            drawRobotPalmChassis(ctx, armRightEndX, armRightEndY, -0.2, 36, userColor);

            // Braço esquerdo de robô se preparando
            let armLeftEndX = cx - bottleW * 0.85;
            let armLeftEndY = baseY - (bottleH * 0.3) * ease;
            drawRobotForearm(ctx, cx - W * 0.38, baseY, armLeftEndX, armLeftEndY, 44, userColor);
            drawRobotPalmChassis(ctx, armLeftEndX, armLeftEndY, 0.4, 32, userColor);

            // Garrafa com tampa (Frame 1)
            ctx.save();
            ctx.translate(bX, bY);
            ctx.rotate(bRot);
            if (IMAGE_ASSETS.juggernaut_bottle_f1 && IMAGE_ASSETS.juggernaut_bottle_f1.complete) {
                ctx.drawImage(IMAGE_ASSETS.juggernaut_bottle_f1, -bottleW / 2, -bottleH / 2, bottleW, bottleH);
            }
            ctx.restore();

            // Dedos de robô da mão direita segurando a garrafa pela frente com outline personalizado
            drawRobotGrippingFingers(ctx, armRightEndX, armRightEndY, bX, bY, bottleW, userColor, true);

        } else if (p < 0.46) {
            // ================= FASE 2: RETIRANDO A TAMPA (FRAME 2 & BOTTLEE TOP) =================
            let t2 = (p - 0.28) / (0.46 - 0.28);
            let bY = baseY - bottleH * 0.52;
            let bX = cx + bottleW * 0.12;
            let bRot = -0.04;
            let isCapPopped = (p >= 0.35);

            let capNeckX = bX - 3;
            let capNeckY = bY - bottleH * 0.46;

            // Braço direito firme segurando a garrafa
            let armRightEndX = bX + bottleW * 0.42;
            let armRightEndY = bY + bottleH * 0.18;
            drawRobotForearm(ctx, cx + W * 0.38, baseY, armRightEndX, armRightEndY, 48, userColor);
            drawRobotPalmChassis(ctx, armRightEndX, armRightEndY, -0.2, 36, userColor);

            // Braço esquerdo alcançando e puxando a tampa
            let reachProgress = Math.min(1, (p - 0.28) / 0.07);
            let armLeftTargetX = isCapPopped ? (capNeckX - 85 - (p - 0.35) * 320) : (capNeckX - 16);
            let armLeftTargetY = isCapPopped ? (capNeckY - 60 - (p - 0.35) * 180) : (capNeckY - 4);
            drawRobotForearm(ctx, cx - W * 0.38, baseY, armLeftTargetX, armLeftTargetY, 44, userColor);

            // Garrafa: Frame 1 antes do pop, Frame 2 depois do pop!
            ctx.save();
            ctx.translate(bX, bY);
            ctx.rotate(bRot);
            let bottleImg = isCapPopped ? IMAGE_ASSETS.juggernaut_bottle_f2 : IMAGE_ASSETS.juggernaut_bottle_f1;
            if (bottleImg && bottleImg.complete) {
                ctx.drawImage(bottleImg, -bottleW / 2, -bottleH / 2, bottleW, bottleH);
            }
            ctx.restore();

            // Tampa (Bottlee Top) voando pelo ar após o pop com giro e gravidade
            if (isCapPopped) {
                let dtCap = (timer - 1.05);
                let capFlightX = capNeckX - dtCap * 520;
                let capFlightY = capNeckY - dtCap * 440 + 0.5 * 1350 * dtCap * dtCap;
                let capRot = dtCap * 18;
                let capSize = 48;

                ctx.save();
                ctx.translate(capFlightX, capFlightY);
                ctx.rotate(capRot);
                if (IMAGE_ASSETS.bottlee_top && IMAGE_ASSETS.bottlee_top.complete) {
                    ctx.drawImage(IMAGE_ASSETS.bottlee_top, -capSize / 2, -capSize / 2, capSize, capSize);
                }
                ctx.restore();

                // Flash luminoso e partículas de gás no bocal da garrafa
                if (p <= 0.40) {
                    let flashP = 1 - (p - 0.35) / 0.05;
                    ctx.fillStyle = `rgba(255, 255, 255, ${flashP * 0.9})`;
                    ctx.shadowColor = '#facc15';
                    ctx.shadowBlur = 24;
                    ctx.beginPath();
                    ctx.arc(capNeckX, capNeckY, 22 * flashP + 8, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;
                }
            } else {
                // Mão esquerda agarrando a tampa
                drawRobotLeftHandRemovingCap(ctx, capNeckX, capNeckY, reachProgress, userColor);
            }

            // Partículas de gás saindo do bocal
            perkDrinkFizzParticles.forEach(fp => {
                let fAlpha = Math.max(0, 1 - fp.life / fp.maxLife);
                ctx.fillStyle = fp.color;
                ctx.globalAlpha = fAlpha;
                ctx.beginPath();
                ctx.arc(capNeckX + fp.x, capNeckY + fp.y, fp.size, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1.0;

            // Dedos da mão direita envolvendo a garrafa
            drawRobotGrippingFingers(ctx, armRightEndX, armRightEndY, bX, bY, bottleW, userColor, true);

        } else if (p < 0.76) {
            // ================= FASE 3: INCLINANDO E BEBENDO (FRAME 3) =================
            let t3 = (p - 0.46) / (0.76 - 0.46);
            let drinkPhase = Math.sin(t3 * Math.PI);
            let gulpBob = Math.sin(t3 * 22) * 5.5;

            // Garrafa se aproxima da boca / câmera (aumenta escala e inclina)
            let drinkScale = 1.0 + drinkPhase * 0.22;
            let curW = bottleW * drinkScale;
            let curH = bottleH * drinkScale;
            let bX = cx + Math.sin(t3 * Math.PI) * 12;
            let bY = baseY - curH * 0.52 - drinkPhase * 36 + gulpBob;
            let bRot = (drinkPhase * 0.38) + Math.sin(t3 * 18) * 0.03;

            // Braço esquerdo apoiando a garrafa
            let armLeftEndX = bX - curW * 0.38;
            let armLeftEndY = bY + curH * 0.22;
            drawRobotForearm(ctx, cx - W * 0.38, baseY, armLeftEndX, armLeftEndY, 46, userColor);
            drawRobotPalmChassis(ctx, armLeftEndX, armLeftEndY, 0.3, 34, userColor);

            // Braço direito erguendo a base da garrafa para beber
            let armRightEndX = bX + curW * 0.38;
            let armRightEndY = bY + curH * 0.18;
            drawRobotForearm(ctx, cx + W * 0.38, baseY, armRightEndX, armRightEndY, 48, userColor);
            drawRobotPalmChassis(ctx, armRightEndX, armRightEndY, -0.3, 36, userColor);

            // Desenho do Frame 3 (bocal inclinado bebendo)
            ctx.save();
            ctx.translate(bX, bY);
            ctx.rotate(bRot);
            if (IMAGE_ASSETS.juggernaut_bottle_f3 && IMAGE_ASSETS.juggernaut_bottle_f3.complete) {
                ctx.drawImage(IMAGE_ASSETS.juggernaut_bottle_f3, -curW / 2, -curH / 2, curW, curH);
            }
            ctx.restore();

            // Dedos de robô segurando os lados da garrafa na inclinação com contorno personalizado
            drawRobotGrippingFingers(ctx, armRightEndX, armRightEndY, bX, bY, curW, userColor, true);
            drawRobotGrippingFingers(ctx, armLeftEndX, armLeftEndY, bX, bY, curW, userColor, false);

            // Bolhas de gás / carbonatação saindo do bocal
            for (let i = 0; i < 3; i++) {
                let bx = bX + (Math.random() - 0.5) * 28;
                let by = bY - curH * 0.38 + (Math.random() - 0.5) * 18;
                ctx.fillStyle = Math.random() > 0.4 ? '#ffffff' : '#fca5a5';
                ctx.beginPath();
                ctx.arc(bx, by, 2 + Math.random() * 3, 0, Math.PI * 2);
                ctx.fill();
            }

        } else {
            // ================= FASE 4: JOGANDO A BEBIDA FORA (ARREMESSO 3D) =================
            let t4 = (p - 0.76) / (1.0 - 0.76);

            // Garrafa voando para frente e girando, diminuindo de tamanho em perspectiva 3D
            let throwProgress = t4;
            let throwScale = Math.max(0.08, 1.0 - throwProgress * 0.88);
            let curW = bottleW * throwScale;
            let curH = bottleH * throwScale;

            let throwX = cx + throwProgress * 240;
            let throwY = (baseY - bottleH * 0.48) - Math.sin(throwProgress * Math.PI * 0.85) * 260 + throwProgress * 190;
            let throwRot = throwProgress * 15;

            // Rastro / linhas de velocidade de arremesso
            ctx.save();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(cx, baseY - bottleH * 0.48);
            ctx.quadraticCurveTo(cx + 80, baseY - bottleH * 0.7, throwX, throwY);
            ctx.stroke();
            ctx.restore();

            // Desenho da garrafa vazia girando pelo ar
            ctx.save();
            ctx.translate(throwX, throwY);
            ctx.rotate(throwRot);
            ctx.globalAlpha = Math.max(0, 1.0 - throwProgress * 0.3);
            if (IMAGE_ASSETS.juggernaut_bottle_f2 && IMAGE_ASSETS.juggernaut_bottle_f2.complete) {
                ctx.drawImage(IMAGE_ASSETS.juggernaut_bottle_f2, -curW / 2, -curH / 2, curW, curH);
            }
            ctx.restore();

            // Braço direito em pose de arremesso e mão aberta com contorno neon do personagem
            let armThrowEndX = cx + 80 + (1 - throwProgress) * 40;
            let armThrowEndY = baseY - (bottleH * 0.28) * (1 - throwProgress * 0.6);
            drawRobotForearm(ctx, cx + W * 0.38, baseY, armThrowEndX, armThrowEndY, 48, userColor);
            drawRobotHandThrowing(ctx, armThrowEndX, armThrowEndY, -0.4, userColor);

            // Braço esquerdo recolhendo
            let armLeftRetractY = baseY + throwProgress * 120;
            drawRobotForearm(ctx, cx - W * 0.38, baseY, cx - W * 0.25, armLeftRetractY, 44, userColor);
        }

        // ================= BANNER DE ATIVAÇÃO TRIUNFANTE =================
        if (p >= 0.68) {
            let bannerAlpha = Math.min(1, (p - 0.68) / 0.12);
            ctx.save();
            ctx.globalAlpha = bannerAlpha;

            let bx = W / 2, by = H * 0.20;
            let bw = Math.min(540, W - 40);
            let bh = 76;

            ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
            ctx.fillRect(bx - bw / 2, by - bh / 2, bw, bh);
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = 2.5;
            ctx.shadowColor = '#dc2626';
            ctx.shadowBlur = 18;
            ctx.strokeRect(bx - bw / 2, by - bh / 2, bw, bh);
            ctx.shadowBlur = 0;

            if (IMAGE_ASSETS.juggernaut_perk && IMAGE_ASSETS.juggernaut_perk.complete) {
                ctx.drawImage(IMAGE_ASSETS.juggernaut_perk, bx - bw / 2 + 14, by - 26, 52, 52);
            }

            ctx.font = 'bold 16px "Press Start 2P", monospace';
            ctx.fillStyle = '#ef4444';
            ctx.textAlign = 'left';
            ctx.shadowColor = '#dc2626';
            ctx.shadowBlur = 10;
            ctx.fillText('JUGGERNAUT ATIVADO!', bx - bw / 2 + 78, by - 8);
            ctx.shadowBlur = 0;

            ctx.font = 'bold 12px monospace';
            ctx.fillStyle = '#22c55e';
            ctx.fillText('⚡ +100 VIDA MÁXIMA • TOTAL 200 HP', bx - bw / 2 + 78, by + 16);

            ctx.restore();
        }

        ctx.restore();
    }
'''
    content = content.replace(m_ov.group(0), new_overlay_code)

# 6. CHEAT EXECUTION FUNCTION
old_cheat_fn_pattern = r'function executeCheatCommand\(\) \{[\s\S]*?(?=\n    window\.addEventListener\(\'keydown\')'
new_cheat_fn = '''function executeCheatCommand() {
        let inputEl = document.getElementById('cheat-code-input');
        let raw = (inputEl.value || '').trim();
        let upper = raw.toUpperCase();
        let feedback = document.getElementById('cheat-feedback');

        if (!raw) {
            upper = 'APOCALYPSE';
        }

        // CÓDIGO GMMONEY: Adiciona qualquer quantia especificada de dinheiro (ex: GMMONEY 999)
        if (upper.startsWith('GMMONEY')) {
            let match = raw.match(/GMMONEY\\s*(\\d+)/i);
            let amount = 10000;
            if (match && match[1]) {
                amount = parseInt(match[1], 10);
                if (isNaN(amount) || amount < 0) amount = 10000;
            }
            player.points += amount;
            playGenericSound('buy');

            feedback.innerText = `CÓDIGO GMMONEY ATIVADO! +$${amount.toLocaleString('pt-BR')} ADICIONADOS À SUA CONTA! (TOTAL: $${player.points.toLocaleString('pt-BR')})`;
            feedback.className = 'text-xs font-mono font-bold text-emerald-400 mb-4 animate-pulse';

            setTimeout(() => {
                closeCheatModal();
            }, 1200);
            return;
        }

        // CÓDIGO APOCALYPSE: Desbloqueia tudo, colas, armas Packed e Round 19
        if (upper === 'APOCALYPSE') {
            player.perks['SPEED'] = true;
            player.perks['FIRERATE'] = true;
            player.perks['JUGGERNAUT'] = true;
            player.perks['3GUNS'] = true;
            player.maxHealth = 200;
            player.health = 200;
            player.maxWeapons = 3;
            player.points += 20000;

            let w1 = createWeaponInstance('AK47');
            let w2 = createWeaponInstance('AA12');
            let w3 = createWeaponInstance('BARRETT');
            [w1, w2, w3].forEach(w => {
                w.isPaP = true;
                let def = WEAPONS_DATA[w.id];
                w.name = `${w.id} • PACKED`;
                w.mag = def.papMag || Math.floor(w.mag * 1.5);
                w.reserve = def.papReserve || Math.floor(w.reserve * 1.5);
                w.currentMag = w.mag;
                w.currentReserve = w.reserve;
            });
            player.weapons = [w1, w2, w3];
            player.currentWeaponIndex = 0;
            player.isReloading = false;
            stopReloadSound();

            roundData.number = 19;
            roundData.state = 'PRE_ROUND';
            roundData.timer = 4;
            roundData.zombiesToSpawn = 6 + (19 * 4);
            roundData.zombiesSpawned = 0;
            roundData.zombiesAlive = 0;
            roundData.promptedRound20 = false;
            roundData.endlessMode = false;
            zombies = [];
            bullets = [];
            rockProjectiles = [];

            playGenericSound('buy');

            feedback.innerText = 'CÓDIGO APOCALYPSE ATIVADO! COLAS, $20.000, 3 ARMAS PACKED & ROUND 19 LIBERADOS!';
            feedback.className = 'text-xs font-mono font-bold text-emerald-400 mb-4 animate-pulse';

            setTimeout(() => {
                closeCheatModal();
            }, 1200);
            return;
        }

        // Código Inválido
        feedback.innerText = 'CÓDIGO INVÁLIDO! Use APOCALYPSE ou GMMONEY <quantia> (ex: GMMONEY 999)';
        feedback.className = 'text-xs font-mono font-bold text-rose-400 mb-4';
    }'''

content = re.sub(old_cheat_fn_pattern, lambda m: new_cheat_fn, content)

# Save to code.html
with open('code.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: code.html updated completely!")

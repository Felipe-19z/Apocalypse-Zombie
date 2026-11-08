import os
import base64
import re

def get_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

b64_perk = get_b64('juggernaut_perk.png')
b64_can = get_b64('juggernaut_can.png')
b64_mach = get_b64('juggernaut_machine.png')

with open('code.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('code_backup.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 1. ASSET DECLARATIONS & SOUND HELPERS
asset_code = f'''    // ================= RECURSOS VISUAIS JUGGERNAUT (BASE64 & IMAGENS) =================
    const ASSET_B64 = {{
        juggernaut_perk: "{b64_perk}",
        juggernaut_can: "{b64_can}",
        juggernaut_machine: "{b64_mach}"
    }};

    const IMAGE_ASSETS = {{
        juggernaut_perk: new Image(),
        juggernaut_can: new Image(),
        juggernaut_machine: new Image()
    }};

    IMAGE_ASSETS.juggernaut_perk.src = ASSET_B64.juggernaut_perk;
    IMAGE_ASSETS.juggernaut_can.src = ASSET_B64.juggernaut_can;
    IMAGE_ASSETS.juggernaut_machine.src = ASSET_B64.juggernaut_machine;

    // ================= EFEITOS SONOROS DE ABRIR E BEBER JUGGERNAUT =================
    function playCanOpenSound() {{
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {{
            // Clique metálico do anel de abertura
            if (toneSynth) {{
                toneSynth.triggerAttackRelease(["E5", "G5", "C6"], "64n");
            }}
            // Hiss / spray de gás sob pressão (PSSSST!)
            if (audioCtx) {{
                let bufferSize = Math.floor(audioCtx.sampleRate * 0.42);
                let buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
                let data = buffer.getChannelData(0);
                for (let i = 0; i < bufferSize; i++) {{
                    let decay = Math.exp(-i / (audioCtx.sampleRate * 0.085));
                    data[i] = (Math.random() * 2 - 1) * decay;
                }}
                let noise = audioCtx.createBufferSource();
                noise.buffer = buffer;
                let filter = audioCtx.createBiquadFilter();
                filter.type = 'highpass';
                filter.frequency.value = 3400;
                let gain = audioCtx.createGain();
                gain.gain.value = 0.75 * audioSettings.sfxVolume;
                noise.connect(filter);
                filter.connect(gain);
                gain.connect(audioCtx.destination);
                noise.start();
            }}
        }} catch(e) {{}}
    }}

    function playCanDrinkSound() {{
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {{
            if (toneSynth) {{
                toneSynth.triggerAttackRelease("C3", "32n");
                setTimeout(() => {{
                    try {{ if (toneSynth) toneSynth.triggerAttackRelease("D3", "32n"); }} catch(e){{}}
                }}, 170);
                setTimeout(() => {{
                    try {{ if (toneSynth) toneSynth.triggerAttackRelease("E3", "32n"); }} catch(e){{}}
                }}, 340);
            }}
        }} catch(e) {{}}
    }}

    function playPerkActivateSound() {{
        if (!audioInitialized || audioSettings.sfxVolume <= 0) return;
        try {{
            if (toneSynth) {{
                toneSynth.triggerAttackRelease(["C4", "G4", "C5", "E5"], "8n");
            }}
            if (toneLowSynth) {{
                toneLowSynth.triggerAttackRelease("C2", "8n");
            }}
        }} catch(e) {{}}
    }}

    // ================= HITBOX E COLISÃO SÓLIDA DE MÁQUINAS =================
    function resolveBoxCollision(circle, box) {{
        let closestX = Math.max(box.x, Math.min(box.x + box.w, circle.x));
        let closestY = Math.max(box.y, Math.min(box.y + box.h, circle.y));
        let dx = circle.x - closestX;
        let dy = circle.y - closestY;
        let distSq = dx * dx + dy * dy;
        let r = circle.radius || 18;
        if (distSq < r * r) {{
            let dist = Math.sqrt(distSq);
            if (dist > 0.0001) {{
                let overlap = r - dist;
                circle.x += (dx / dist) * overlap;
                circle.y += (dy / dist) * overlap;
            }} else {{
                let left = circle.x - box.x;
                let right = (box.x + box.w) - circle.x;
                let top = circle.y - box.y;
                let bottom = (box.y + box.h) - circle.y;
                let min = Math.min(left, right, top, bottom);
                if (min === left) circle.x = box.x - r;
                else if (min === right) circle.x = box.x + box.w + r;
                else if (min === top) circle.y = box.y - r;
                else circle.y = box.y + box.h + r;
            }}
            return true;
        }}
        return false;
    }}

    function spawnCanFizzParticles(startX, startY) {{
        for (let i = 0; i < 40; i++) {{
            let angle = -Math.PI / 2 + (Math.random() - 0.5) * 1.3;
            let speed = 90 + Math.random() * 150;
            perkDrinkFizzParticles.push({{
                x: startX || 0,
                y: startY || 0,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 50,
                size: 2.2 + Math.random() * 3.8,
                color: Math.random() > 0.35 ? '#ffffff' : (Math.random() > 0.5 ? '#fef08a' : '#f87171'),
                alpha: 1.0,
                life: 0,
                maxLife: 0.45 + Math.random() * 0.5
            }});
        }}
    }}

    function startPerkDrinking(perkType) {{
        player.isDrinkingPerk = true;
        player.perkDrinkTimer = 0;
        player.perkDrinkDuration = 2.4;
        player.perkDrinkType = perkType;
        player.canTabPopped = false;
        player.canDrinkGulpPlayed = false;
        player.perkActivated = false;
        perkDrinkFizzParticles = [];
        playGenericSound('buy');
    }}
'''

target_audio = '''    const audioBuffers = {};
    const audioElements = {};
    let currentReloadSource = null;
    let currentReloadAudioElement = null;
    let bossBgmAudio = null;'''

content = content.replace(target_audio, target_audio + '\n\n' + asset_code)

# 2. GLOBAL VARIABLES
target_stats = 'let battleStats = { startTime: 0, endTime: 0, shotsFired: 0, shotsHit: 0 };'
replacement_stats = '''let battleStats = { startTime: 0, endTime: 0, shotsFired: 0, shotsHit: 0 };
    let perkDrinkFizzParticles = [];'''
content = content.replace(target_stats, replacement_stats)

# 3. PLAYER OBJECT & INTERACTABLES IN initGame()
old_player_init = '''            recoilAccumulator: 0, timeSinceShot: 1000,
            interactProgress: 0, interactingWith: null, regenDelay: 0,
            isSprinting: false, walkCycle: 0,
            muzzleFlashTimer: 0
        };'''

new_player_init = '''            recoilAccumulator: 0, timeSinceShot: 1000,
            interactProgress: 0, interactingWith: null, nearbyInteractable: null, regenDelay: 0,
            isSprinting: false, walkCycle: 0,
            muzzleFlashTimer: 0,
            isDrinkingPerk: false, perkDrinkTimer: 0, perkDrinkDuration: 2.4, perkDrinkType: null,
            canTabPopped: false, canDrinkGulpPlayed: false, perkActivated: false,
            juggernautJustAcquiredTimer: 0
        };'''

content = content.replace(old_player_init, new_player_init)

old_interactables = '''        interactables = [
            { type: 'PERK', perk: 'SPEED', color: '#f1c40f', cost: 3000, name: 'Speed Cola', x: 200, y: 200, w: 70, h: 70 },
            { type: 'PERK', perk: 'FIRERATE', color: '#2ecc71', cost: 2000, name: 'Double Tap', x: MAP_WIDTH-270, y: 200, w: 70, h: 70 },
            { type: 'PERK', perk: 'JUGGERNAUT', color: '#e74c3c', cost: 2500, name: 'Juggernog', x: 200, y: MAP_HEIGHT-270, w: 70, h: 70 },
            { type: 'PERK', perk: '3GUNS', color: '#9b59b6', cost: 4000, name: 'Mule Kick', x: MAP_WIDTH-270, y: MAP_HEIGHT-270, w: 70, h: 70 },
            { type: 'MYSTERY_BOX', color: '#8B4513', cost: 950, name: 'Caixa Misteriosa', x: MAP_WIDTH/2 - 75, y: 300, w: 150, h: 65, state: 'IDLE', timer: 0, weaponShown: null },
            { type: 'PACK_A_PUNCH', color: '#3498db', cost: 5000, name: 'Pack-a-Punch', x: MAP_WIDTH/2 - 75, y: MAP_HEIGHT-300, w: 150, h: 100 }
        ];'''

new_interactables = '''        interactables = [
            { type: 'PERK', perk: 'SPEED', color: '#f1c40f', cost: 3000, name: 'Speed Cola', x: 200, y: 200, w: 70, h: 70, hasHitbox: true },
            { type: 'PERK', perk: 'FIRERATE', color: '#2ecc71', cost: 2000, name: 'Double Tap', x: MAP_WIDTH-270, y: 200, w: 70, h: 70, hasHitbox: true },
            { type: 'PERK', perk: 'JUGGERNAUT', color: '#e74c3c', cost: 2500, name: 'Juggernaut', x: 200, y: MAP_HEIGHT-290, w: 76, h: 96, hasHitbox: true },
            { type: 'PERK', perk: '3GUNS', color: '#9b59b6', cost: 4000, name: 'Mule Kick', x: MAP_WIDTH-270, y: MAP_HEIGHT-270, w: 70, h: 70, hasHitbox: true },
            { type: 'MYSTERY_BOX', color: '#8B4513', cost: 950, name: 'Caixa Misteriosa', x: MAP_WIDTH/2 - 75, y: 300, w: 150, h: 65, state: 'IDLE', timer: 0, weaponShown: null, hasHitbox: true },
            { type: 'PACK_A_PUNCH', color: '#3498db', cost: 5000, name: 'Pack-a-Punch', x: MAP_WIDTH/2 - 75, y: MAP_HEIGHT-300, w: 150, h: 100, hasHitbox: true }
        ];'''

content = content.replace(old_interactables, new_interactables)

# 4. ZOMBIE HITBOX COLLISION
old_zombie_move = '''            if (dist > this.radius + player.radius) {
                this.x += (dx / dist) * this.speed * dt;
                this.y += (dy / dist) * this.speed * dt;
            }'''

new_zombie_move = '''            if (dist > this.radius + player.radius) {
                this.x += (dx / dist) * this.speed * dt;
                this.y += (dy / dist) * this.speed * dt;
            }
            
            // Hitbox de máquinas: zumbis não podem passar por cima nem atravessar
            for (let obj of interactables) {
                if (obj.hasHitbox) {
                    resolveBoxCollision(this, obj);
                }
            }'''

content = content.replace(old_zombie_move, new_zombie_move)

# 5. BOSS HITBOX COLLISION
old_boss_move = '''            this.x += (dx / dist) * this.speed * dt;
            this.y += (dy / dist) * this.speed * dt;'''
new_boss_move = '''            this.x += (dx / dist) * this.speed * dt;
            this.y += (dy / dist) * this.speed * dt;
            for (let obj of interactables) {
                if (obj.hasHitbox) {
                    resolveBoxCollision(this, obj);
                }
            }'''
content = content.replace(old_boss_move, new_boss_move)

# 6. SWITCH WEAPON / SHOOT / RELOAD CHECKS FOR DRINKING
old_switch = '''    function switchWeapon(index) {
        if (player.isReloading) return;'''
new_switch = '''    function switchWeapon(index) {
        if (player.isReloading || player.isDrinkingPerk) return;'''
content = content.replace(old_switch, new_switch)

old_start_reload = '''    function startReload() {
        if (player.isReloading) return;'''
new_start_reload = '''    function startReload() {
        if (player.isReloading || player.isDrinkingPerk) return;'''
content = content.replace(old_start_reload, new_start_reload)

# 7. HANDLE INTERACTIONS - APPROPRIATE DISTANCE & DRINKING PERK
old_interactions = '''    function handleInteractions(dt) {
        if (!keys['f']) {
            player.interactProgress = 0;
            player.interactingWith = null;
            return;
        }

        let nearest = null; let minDist = 130;
        for (let obj of interactables) {
            let cx = obj.x + obj.w / 2; let cy = obj.y + obj.h / 2;
            let dist = Math.hypot(player.x - cx, player.y - cy);
            if (dist < minDist) { minDist = dist; nearest = obj; }
        }

        if (nearest) {
            player.interactingWith = nearest;
            player.interactProgress += dt;
            
            if (player.interactProgress >= 1.8) {
                player.interactProgress = 0;
                if (nearest.type === 'PERK' && player.points >= nearest.cost && !player.perks[nearest.perk]) {
                    player.points -= nearest.cost;
                    player.perks[nearest.perk] = true;
                    playGenericSound('buy');
                    if (nearest.perk === 'JUGGERNAUT') { player.maxHealth = 200; player.health += 100; }
                    if (nearest.perk === '3GUNS') player.maxWeapons = 3;
                }'''

new_interactions = '''    function handleInteractions(dt) {
        // Encontra a máquina mais próxima para aproximação e interação
        let nearest = null; let minDist = 125;
        for (let obj of interactables) {
            let cx = obj.x + obj.w / 2; let cy = obj.y + obj.h / 2;
            let dist = Math.hypot(player.x - cx, player.y - cy);
            if (dist < minDist) { minDist = dist; nearest = obj; }
        }
        player.nearbyInteractable = nearest;

        if (!keys['f']) {
            player.interactProgress = 0;
            player.interactingWith = null;
            return;
        }

        if (nearest) {
            player.interactingWith = nearest;
            player.interactProgress += dt;
            
            if (player.interactProgress >= 1.8) {
                player.interactProgress = 0;
                if (nearest.type === 'PERK' && player.points >= nearest.cost && !player.perks[nearest.perk]) {
                    if (nearest.perk === 'JUGGERNAUT') {
                        if (!player.isDrinkingPerk) {
                            player.points -= nearest.cost;
                            startPerkDrinking('JUGGERNAUT');
                        }
                    } else {
                        player.points -= nearest.cost;
                        player.perks[nearest.perk] = true;
                        playGenericSound('buy');
                        if (nearest.perk === '3GUNS') player.maxWeapons = 3;
                    }
                }'''

content = content.replace(old_interactions, new_interactions)

# 8. PLAYER HITBOX COLLISION & DRINKING PERK UPDATE
old_player_move = '''        player.x += vx * currentSpeed * dt;
        player.y += vy * currentSpeed * dt;
        player.x = Math.max(player.radius, Math.min(MAP_WIDTH - player.radius, player.x));
        player.y = Math.max(player.radius, Math.min(MAP_HEIGHT - player.radius, player.y));'''

new_player_move = '''        player.x += vx * currentSpeed * dt;
        player.y += vy * currentSpeed * dt;

        // Hitbox sólida de máquinas (o jogador não pode passar por cima)
        for (let obj of interactables) {
            if (obj.hasHitbox) {
                resolveBoxCollision(player, obj);
            }
        }

        player.x = Math.max(player.radius, Math.min(MAP_WIDTH - player.radius, player.x));
        player.y = Math.max(player.radius, Math.min(MAP_HEIGHT - player.radius, player.y));

        // Atualização da animação e efeitos de beber Perk (Juggernaut)
        if (player.isDrinkingPerk) {
            player.perkDrinkTimer += dt;
            let t = player.perkDrinkTimer;

            // t = 0.55s: Abre a lata (som do anel + spray de gás sob pressão)
            if (t >= 0.55 && !player.canTabPopped) {
                player.canTabPopped = true;
                playCanOpenSound();
                spawnCanFizzParticles();
            }

            // t = 1.05s: Som de beber / goles refrescantes
            if (t >= 1.05 && !player.canDrinkGulpPlayed) {
                player.canDrinkGulpPlayed = true;
                playCanDrinkSound();
            }

            // t = 1.85s: Ativação oficial do Juggernaut
            if (t >= 1.85 && !player.perkActivated) {
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

            if (t >= player.perkDrinkDuration) {
                player.isDrinkingPerk = false;
                player.perkDrinkTimer = 0;
            }
        }

        if (player.juggernautJustAcquiredTimer > 0) {
            player.juggernautJustAcquiredTimer -= dt;
        }

        // Atualização das partículas de gás da lata aberta
        for (let i = perkDrinkFizzParticles.length - 1; i >= 0; i--) {
            let fp = perkDrinkFizzParticles[i];
            fp.life += dt;
            fp.x += fp.vx * dt;
            fp.y += fp.vy * dt;
            fp.vy += 70 * dt;
            if (fp.life >= fp.maxLife) perkDrinkFizzParticles.splice(i, 1);
        }'''

content = content.replace(old_player_move, new_player_move)

# 9. DISALLOW SHOOTING WHILE DRINKING
old_shoot_check = '''        if (!player.isReloading) {
            let rate = weapon.fireRate;
            if (player.perks['FIRERATE']) rate *= 0.8;
            if (mouse.leftDown && !player.isSprinting && player.timeSinceShot >= rate) {'''

new_shoot_check = '''        if (!player.isReloading && !player.isDrinkingPerk) {
            let rate = weapon.fireRate;
            if (player.perks['FIRERATE']) rate *= 0.8;
            if (mouse.leftDown && !player.isSprinting && player.timeSinceShot >= rate) {'''

content = content.replace(old_shoot_check, new_shoot_check)

# 10. TOP-DOWN PLAYER VIEW WHILE DRINKING
old_player_tactical_pose = '''        } else {
            // ================= POSES DE SEGURAR EM MIRA/PARADO =================
            if (player.walkCycle > 0) {
                bodyBob = Math.abs(Math.sin(player.walkCycle * 2)) * 1.2;
            }'''

new_player_tactical_pose = '''        } else if (player.isDrinkingPerk) {
            // ================= POSE BEBENDO A LATA DE JUGGERNAUT =================
            let dp = player.perkDrinkTimer / (player.perkDrinkDuration || 2.4);
            let bob = Math.sin(dp * Math.PI * 4) * 2;
            gunOffsetX = 0; gunOffsetY = 0; gunOffsetAngle = 0;
            handL.x = 15; handL.y = -6 + bob;
            handR.x = 15; handR.y = 6 + bob;
        } else {
            // ================= POSES DE SEGURAR EM MIRA/PARADO =================
            if (player.walkCycle > 0) {
                bodyBob = Math.abs(Math.sin(player.walkCycle * 2)) * 1.2;
            }'''

content = content.replace(old_player_tactical_pose, new_player_tactical_pose)

# Gun drawing in drawPlayerTactical
old_gun_draw = '''        // 2. BRAÇOS, MÃOS, ARMA E PENTE (DESENHADOS DEBAIXO DO CORPO DO BONECO)
        // Modelo da Arma
        ctx.save();
        ctx.translate(gunOffsetX, gunOffsetY);
        ctx.rotate(gunOffsetAngle);
        drawWeaponModel(ctx, cw.id, isPaP, weaponOpts);'''

new_gun_draw = '''        // 2. BRAÇOS, MÃOS, ARMA E PENTE (DESENHADOS DEBAIXO DO CORPO DO BONECO)
        // Se estiver bebendo Juggernaut, desenha a mini-lata na mão em vez da arma
        if (player.isDrinkingPerk) {
            ctx.save();
            ctx.translate(16, 0);
            ctx.fillStyle = '#b91c1c';
            ctx.beginPath();
            ctx.arc(0, 0, 7.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#d4af37';
            ctx.lineWidth = 1.8;
            ctx.stroke();
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(-5, -2, 10, 4);
            ctx.fillStyle = '#facc15';
            ctx.beginPath();
            ctx.arc(1, 0, 2.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        } else {
            // Modelo da Arma
            ctx.save();
            ctx.translate(gunOffsetX, gunOffsetY);
            ctx.rotate(gunOffsetAngle);
            drawWeaponModel(ctx, cw.id, isPaP, weaponOpts);'''

content = content.replace(old_gun_draw, new_gun_draw)

# Close the else block for gun drawing
old_gun_draw_close = '''            ctx.shadowBlur = 0;
            ctx.restore();
        }
        ctx.restore();'''

new_gun_draw_close = '''            ctx.shadowBlur = 0;
            ctx.restore();
        }
        ctx.restore();
        }''' # One more brace to close the if (!player.isDrinkingPerk) else block

content = content.replace(old_gun_draw_close, new_gun_draw_close)

# 11. REMODELED JUGGERNAUT VENDING MACHINE RENDERING & PROCEDURAL FALLBACKS
old_vending_fn = '''    // ================= DESENHO DAS MÁQUINAS DE COLAS =================
    function drawPerkVendingMachine(ctx, obj) {'''

new_vending_fn = '''    // ================= DESENHO PROCEDURAL DA LATA CASO IMAGEM DEMORE =================
    function drawProceduralJuggernautCan(ctx, x, y, w, h) {
        ctx.save();
        // Base e corpo carmesim
        ctx.fillStyle = '#991b1b';
        ctx.fillRect(x, y + 16, w, h - 32);

        // Borda dourada superior e inferior
        ctx.fillStyle = '#eab308';
        ctx.fillRect(x + 4, y, w - 8, 16);
        ctx.fillRect(x + 4, y + h - 16, w - 8, 16);
        ctx.strokeStyle = '#fef08a';
        ctx.lineWidth = 2;
        ctx.strokeRect(x + 4, y, w - 8, 16);
        ctx.strokeRect(x + 4, y + h - 16, w - 8, 16);

        // Faixa branca central
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(x, y + h * 0.22, w, h * 0.28);

        // Brasão central Juggernaut
        let cx = x + w / 2;
        let cy = y + h * 0.52;
        ctx.fillStyle = '#7f1d1d';
        ctx.beginPath();
        ctx.arc(cx, cy, w * 0.35, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#eab308';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Cruz médica branca e projétil
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 5, cy - 18, 10, 36);
        ctx.fillRect(cx - 18, cy - 5, 36, 10);
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.ellipse(cx, cy, 5, 20, Math.PI / 4, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }

    // ================= DESENHO PROCEDURAL DA MÁQUINA CASO IMAGEM DEMORE =================
    function drawProceduralJuggernautMachine(ctx, obj, drawX, drawY, drawW, drawH) {
        ctx.save();
        let cx = drawX + drawW / 2;

        // Placa circular iluminada no topo (marca Juggernog)
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(cx, drawY + 14, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#b91c1c';
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = '#b91c1c';
        ctx.fillRect(cx - 3, drawY + 6, 6, 16);
        ctx.fillRect(cx - 8, drawY + 11, 16, 6);

        // Gabinete clássico vermelho curvado (1950s)
        let cabY = drawY + 30;
        let cabH = drawH - 30;
        ctx.fillStyle = '#b91c1c';
        ctx.fillRect(drawX, cabY, drawW, cabH);
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 3;
        ctx.strokeRect(drawX, cabY, drawW, cabH);

        // Marquee iluminado superior com "JUGGERNAUT"
        ctx.fillStyle = '#f8fafc';
        ctx.fillRect(drawX + 6, cabY + 6, drawW - 12, 18);
        ctx.strokeStyle = '#94a3b8';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(drawX + 6, cabY + 6, drawW - 12, 18);
        ctx.font = 'bold 8px "Press Start 2P", monospace';
        ctx.fillStyle = '#b91c1c';
        ctx.textAlign = 'center';
        ctx.fillText('JUGG', cx, cabY + 19);

        // Painel console preto dos botões
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(drawX + 10, cabY + 32, drawW - 20, 26);
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 1;
        ctx.strokeRect(drawX + 10, cabY + 32, drawW - 20, 26);

        // Base cromada
        ctx.fillStyle = '#94a3b8';
        ctx.fillRect(drawX + 2, drawY + drawH - 12, drawW - 4, 12);
        ctx.restore();
    }

    // ================= DESENHO REMODELADO DA MÁQUINA JUGGERNAUT (IMAGEM 2) =================
    function drawJuggernautMachineRemodeled(ctx, obj) {
        ctx.save();
        let pulse = Math.sin(performance.now() * 0.005);
        let glowAlpha = 0.22 + pulse * 0.08;

        // 1. Poça de néon vermelho no chão (iluminação ambiente atmosférica)
        let floorGrad = ctx.createRadialGradient(obj.x + obj.w / 2, obj.y + obj.h - 8, 15, obj.x + obj.w / 2, obj.y + obj.h - 8, 90);
        floorGrad.addColorStop(0, `rgba(239, 68, 68, ${glowAlpha * 1.5})`);
        floorGrad.addColorStop(0.65, `rgba(185, 28, 28, ${glowAlpha * 0.7})`);
        floorGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = floorGrad;
        ctx.beginPath();
        ctx.ellipse(obj.x + obj.w / 2, obj.y + obj.h - 4, obj.w * 0.95, 26, 0, 0, Math.PI * 2);
        ctx.fill();

        // 2. Sombra de contato no chão
        ctx.fillStyle = 'rgba(0, 0, 0, 0.55)';
        ctx.beginPath();
        ctx.ellipse(obj.x + obj.w / 2, obj.y + obj.h - 2, obj.w * 0.52, 9, 0, 0, Math.PI * 2);
        ctx.fill();

        // 3. Desenho da máquina remodelada (Sprite 2.5D com placa superior estendida)
        let drawY = obj.y - 28;
        let drawH = obj.h + 28;
        let drawW = obj.w + 4;
        let drawX = obj.x - 2;

        if (IMAGE_ASSETS.juggernaut_machine && IMAGE_ASSETS.juggernaut_machine.complete && IMAGE_ASSETS.juggernaut_machine.naturalWidth > 0) {
            ctx.drawImage(IMAGE_ASSETS.juggernaut_machine, drawX, drawY, drawW, drawH);
        } else {
            drawProceduralJuggernautMachine(ctx, obj, drawX, drawY, drawW, drawH);
        }

        // 4. Overlays luminosos dinâmicos:
        // Halo pulsante na placa circular do topo (logo Juggernog)
        let topSignX = obj.x + obj.w / 2;
        let topSignY = drawY + 14;
        let signHalo = ctx.createRadialGradient(topSignX, topSignY, 2, topSignX, topSignY, 24);
        signHalo.addColorStop(0, 'rgba(255, 255, 255, 0.45)');
        signHalo.addColorStop(0.5, 'rgba(239, 68, 68, 0.35)');
        signHalo.addColorStop(1, 'rgba(239, 68, 68, 0)');
        ctx.fillStyle = signHalo;
        ctx.beginPath();
        ctx.arc(topSignX, topSignY, 24, 0, Math.PI * 2);
        ctx.fill();

        // Botões iluminados (3 LEDs vermelhos acesos no painel preto)
        let btnY = drawY + drawH * 0.46;
        for (let b = -1; b <= 1; b++) {
            let bx = topSignX + b * 9;
            ctx.fillStyle = '#ef4444';
            ctx.shadowColor = '#dc2626';
            ctx.shadowBlur = 6;
            ctx.fillRect(bx - 2.5, btnY, 5, 6);
            ctx.fillStyle = '#fca5a5';
            ctx.fillRect(bx - 1.5, btnY + 1, 3, 2);
            ctx.shadowBlur = 0;
        }

        // 5. Rótulo superior & Preço
        ctx.font = 'bold 11px "Press Start 2P", monospace';
        ctx.fillStyle = '#ef4444';
        ctx.textAlign = 'center';
        ctx.shadowColor = '#b91c1c';
        ctx.shadowBlur = 10;
        ctx.fillText('JUGGERNAUT', obj.x + obj.w / 2, drawY - 12);
        ctx.shadowBlur = 0;

        if (player && player.perks && player.perks['JUGGERNAUT']) {
            ctx.font = 'bold 10px monospace';
            ctx.fillStyle = '#10b981';
            ctx.fillText('[EQUIPADO ✓]', obj.x + obj.w / 2, obj.y + obj.h + 16);
        } else {
            ctx.font = 'bold 11px monospace';
            ctx.fillStyle = '#fbbf24';
            ctx.fillText(`$${obj.cost}`, obj.x + obj.w / 2, obj.y + obj.h + 16);
        }

        // 6. Tooltip de Aproximação e Interação
        if (player && player.nearbyInteractable === obj && (!player.interactingWith || player.interactProgress <= 0)) {
            let badgeY = drawY - 30;
            let badgeText = (player.perks && player.perks['JUGGERNAUT']) 
                ? 'JUGGERNAUT [JÁ EQUIPADO]' 
                : (player.points < obj.cost 
                    ? `[F] JUGGERNAUT ($${obj.cost}) - PONTOS INSUFICIENTES`
                    : `[SEGURAR F] COMPRAR JUGGERNAUT ($${obj.cost})`);

            ctx.font = 'bold 11px monospace';
            let tw = ctx.measureText(badgeText).width + 24;
            let th = 22;

            ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
            ctx.fillRect(topSignX - tw / 2, badgeY - th / 2, tw, th);
            ctx.strokeStyle = (player.perks && player.perks['JUGGERNAUT']) ? '#10b981' : (player.points < obj.cost ? '#eab308' : '#ef4444');
            ctx.lineWidth = 1.5;
            ctx.strokeRect(topSignX - tw / 2, badgeY - th / 2, tw, th);

            ctx.fillStyle = (player.perks && player.perks['JUGGERNAUT']) ? '#34d399' : (player.points < obj.cost ? '#fde047' : '#ffffff');
            ctx.fillText(badgeText, topSignX, badgeY + 4);
        }

        ctx.restore();
    }

    // ================= DESENHO DAS MÁQUINAS DE COLAS =================
    function drawPerkVendingMachine(ctx, obj) {
        if (obj.perk === 'JUGGERNAUT') {
            drawJuggernautMachineRemodeled(ctx, obj);
            return;
        }'''

content = content.replace(old_vending_fn, new_vending_fn)

# 12. FIRST-PERSON CAN DRINKING OVERLAY & ANIMATION
drinking_overlay_code = '''    // ================= ANIMAÇÃO DE ABERTURA E BEBIDA DA LATA JUGGERNAUT (1ª PESSOA) =================
    function drawPerkDrinkingOverlay(ctx) {
        if (!player || !player.isDrinkingPerk) return;

        let W = canvas.width;
        let H = canvas.height;
        let timer = player.perkDrinkTimer;
        let dur = player.perkDrinkDuration || 2.4;
        let p = Math.min(1, Math.max(0, timer / dur));

        let cx = W * 0.5;
        let baseY = H;
        let canW = Math.min(180, Math.max(125, W * 0.18));
        let canH = canW * (361 / 190);

        let canY, canRot;

        if (p < 0.22) {
            let t = p / 0.22;
            let ease = Math.sin(t * Math.PI / 2);
            canY = baseY + (1 - ease) * (canH + 60) - canH * 0.52;
            canRot = 0;
        } else if (p < 0.40) {
            canY = baseY - canH * 0.52;
            canRot = 0;
        } else if (p < 0.78) {
            let t = (p - 0.40) / 0.38;
            let drinkPhase = Math.sin(t * Math.PI);
            canRot = drinkPhase * 0.44; // ~25 graus de inclinação
            canY = baseY - canH * 0.52 - drinkPhase * 28 + Math.sin(t * 18) * 3.5;
        } else {
            let t = (p - 0.78) / 0.22;
            canY = baseY - canH * 0.52 + t * (canH + 80);
            canRot = (1 - t) * 0.12;
        }

        ctx.save();

        // Vinheta vermelha / foco de beber perk
        let vigAlpha = Math.sin(p * Math.PI) * 0.35;
        let vigGrad = ctx.createRadialGradient(W / 2, H / 2, W * 0.25, W / 2, H / 2, W * 0.75);
        vigGrad.addColorStop(0, 'rgba(0,0,0,0)');
        vigGrad.addColorStop(1, `rgba(185, 28, 28, ${vigAlpha})`);
        ctx.fillStyle = vigGrad;
        ctx.fillRect(0, 0, W, H);

        let sleeveColor = characterConfig.color || '#38bdf8';
        let gloveColor = '#1e293b';
        let skinColor = '#cbd5e1';

        // 1. BRAÇOS E MÃOS SEGURANDO A LATA (Visão em primeira pessoa imersiva)
        // Braço esquerdo (apoia a lateral e base da lata)
        ctx.save();
        ctx.fillStyle = sleeveColor;
        ctx.beginPath();
        ctx.moveTo(cx - canW * 1.1, baseY);
        ctx.lineTo(cx - canW * 0.28, canY + canH * 0.22);
        ctx.lineTo(cx - canW * 0.45, canY + canH * 0.38);
        ctx.lineTo(cx - canW * 1.35, baseY);
        ctx.closePath();
        ctx.fill();

        // Luva / mão esquerda segurando a lata
        ctx.fillStyle = gloveColor;
        ctx.beginPath();
        ctx.ellipse(cx - canW * 0.35, canY + canH * 0.22, 16, 26, -0.2, 0, Math.PI * 2);
        ctx.fill();
        // Dedos esquerdos abraçando a frente da lata
        for (let f = 0; f < 3; f++) {
            ctx.fillStyle = skinColor;
            ctx.beginPath();
            ctx.ellipse(cx - canW * 0.35 + 8, canY + canH * 0.14 + f * 11, 7, 5, 0.2, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();

        // Braço direito
        ctx.save();
        ctx.fillStyle = sleeveColor;
        ctx.beginPath();
        if (p < 0.38) {
            // Mão direita esticada até o topo da lata para puxar o anel
            ctx.moveTo(cx + canW * 1.1, baseY);
            ctx.lineTo(cx + canW * 0.15, canY - canH * 0.44);
            ctx.lineTo(cx + canW * 0.32, canY - canH * 0.32);
            ctx.lineTo(cx + canW * 1.35, baseY);
            ctx.closePath();
            ctx.fill();

            // Luva e dedos puxando o lacre do topo
            ctx.fillStyle = gloveColor;
            ctx.beginPath();
            ctx.ellipse(cx + canW * 0.15, canY - canH * 0.44, 14, 18, 0.4, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = skinColor;
            ctx.beginPath();
            ctx.ellipse(cx + canW * 0.08, canY - canH * 0.47, 7, 5, -0.3, 0, Math.PI * 2);
            ctx.fill();
        } else {
            // Mão direita apoiando o outro lado da lata durante o gole
            ctx.moveTo(cx + canW * 1.1, baseY);
            ctx.lineTo(cx + canW * 0.35, canY + canH * 0.18);
            ctx.lineTo(cx + canW * 0.52, canY + canH * 0.35);
            ctx.lineTo(cx + canW * 1.35, baseY);
            ctx.closePath();
            ctx.fill();

            ctx.fillStyle = gloveColor;
            ctx.beginPath();
            ctx.ellipse(cx + canW * 0.38, canY + canH * 0.20, 16, 26, 0.2, 0, Math.PI * 2);
            ctx.fill();
            for (let f = 0; f < 3; f++) {
                ctx.fillStyle = skinColor;
                ctx.beginPath();
                ctx.ellipse(cx + canW * 0.38 - 8, canY + canH * 0.12 + f * 11, 7, 5, -0.2, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        ctx.restore();

        // 2. DESENHO DA LATA DE JUGGERNAUT
        ctx.save();
        ctx.translate(cx, canY);
        ctx.rotate(canRot);

        if (IMAGE_ASSETS.juggernaut_can && IMAGE_ASSETS.juggernaut_can.complete && IMAGE_ASSETS.juggernaut_can.naturalWidth > 0) {
            ctx.drawImage(IMAGE_ASSETS.juggernaut_can, -canW / 2, -canH / 2, canW, canH);
        } else {
            drawProceduralJuggernautCan(ctx, -canW / 2, -canH / 2, canW, canH);
        }

        // Brilho especular cilíndrico
        let shineGrad = ctx.createLinearGradient(-canW / 2, 0, canW / 2, 0);
        shineGrad.addColorStop(0, 'rgba(255,255,255,0)');
        shineGrad.addColorStop(0.35, 'rgba(255,255,255,0.18)');
        shineGrad.addColorStop(0.55, 'rgba(255,255,255,0)');
        shineGrad.addColorStop(0.85, 'rgba(0,0,0,0.22)');
        ctx.fillStyle = shineGrad;
        ctx.fillRect(-canW * 0.46, -canH * 0.44, canW * 0.92, canH * 0.88);

        // Lacre metálico aberto & bocal
        if (player.canTabPopped) {
            ctx.fillStyle = '#450a0a';
            ctx.beginPath();
            ctx.ellipse(canW * 0.05, -canH * 0.44, 9, 5, 0.1, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#fef08a';
            ctx.beginPath();
            ctx.ellipse(canW * 0.05, -canH * 0.44, 6, 2.5, 0.1, 0, Math.PI * 2);
            ctx.fill();

            ctx.save();
            ctx.translate(canW * 0.12, -canH * 0.46);
            ctx.rotate(-0.55);
            ctx.fillStyle = '#facc15';
            ctx.strokeStyle = '#ca8a04';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(-4, -10, 8, 12);
            ctx.fillRect(-4, -10, 8, 12);
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(0, -6, 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Flash de abertura do anel no t = 0.22s - 0.34s
        if (p >= 0.22 && p <= 0.34) {
            let flashP = 1 - (p - 0.22) / 0.12;
            ctx.fillStyle = `rgba(255, 255, 255, ${flashP * 0.85})`;
            ctx.shadowColor = '#facc15';
            ctx.shadowBlur = 18;
            ctx.beginPath();
            ctx.arc(canW * 0.08, -canH * 0.45, 18 * flashP + 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // Partículas de gás/fizz saindo da lata
        perkDrinkFizzParticles.forEach(fp => {
            let fAlpha = Math.max(0, 1 - fp.life / fp.maxLife);
            ctx.fillStyle = fp.color;
            ctx.globalAlpha = fAlpha;
            ctx.beginPath();
            ctx.arc(canW * 0.06 + fp.x, -canH * 0.44 + fp.y, fp.size, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.globalAlpha = 1.0;

        ctx.restore();

        // 3. BANNER DE ATIVAÇÃO TRIUNFANTE NA FASE FINAL
        if (p >= 0.75) {
            let bannerAlpha = Math.min(1, (p - 0.75) / 0.1);
            ctx.save();
            ctx.globalAlpha = bannerAlpha;

            let bx = W / 2, by = H * 0.22;
            let bw = Math.min(520, W - 40);
            let bh = 70;

            // Fundo escuro com borda carmesim e brilho
            ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
            ctx.fillRect(bx - bw / 2, by - bh / 2, bw, bh);
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = 2.5;
            ctx.shadowColor = '#dc2626';
            ctx.shadowBlur = 16;
            ctx.strokeRect(bx - bw / 2, by - bh / 2, bw, bh);
            ctx.shadowBlur = 0;

            // Ícone do Perk no banner (Imagem 3 sem fundo preto)
            if (IMAGE_ASSETS.juggernaut_perk && IMAGE_ASSETS.juggernaut_perk.complete) {
                ctx.drawImage(IMAGE_ASSETS.juggernaut_perk, bx - bw / 2 + 12, by - 24, 48, 48);
            }

            // Textos do Banner
            ctx.font = 'bold 16px "Press Start 2P", monospace';
            ctx.fillStyle = '#ef4444';
            ctx.textAlign = 'left';
            ctx.shadowColor = '#dc2626';
            ctx.shadowBlur = 10;
            ctx.fillText('JUGGERNAUT ATIVADO!', bx - bw / 2 + 70, by - 6);
            ctx.shadowBlur = 0;

            ctx.font = 'bold 12px monospace';
            ctx.fillStyle = '#22c55e';
            ctx.fillText('⚡ +100 VIDA MÁXIMA • TOTAL 200 HP', bx - bw / 2 + 70, by + 16);

            ctx.restore();
        }

        ctx.restore();
    }
'''

# Add drinking overlay function right before function draw()
content = content.replace('    function draw() {', drinking_overlay_code + '\n    function draw() {')

# Call drawPerkDrinkingOverlay(ctx) in draw() right after ctx.restore()
old_hud_start = '''        ctx.restore();

        // ================= HUD ================='''

new_hud_start = '''        ctx.restore();

        // Animação em 1ª Pessoa da lata de Juggernaut abrindo e bebendo
        drawPerkDrinkingOverlay(ctx);

        // ================= HUD ================='''

content = content.replace(old_hud_start, new_hud_start)

# 13. HUD PERK ICON (IMAGEM 3 SEM FUNDO PRETO)
badge_fallback = '''    function drawJuggernautBadgeProcedural(ctx, x, y, w, h) {
        ctx.save();
        ctx.fillStyle = '#b91c1c';
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + w, y);
        ctx.lineTo(x + w, y + h * 0.7);
        ctx.lineTo(x + w / 2, y + h);
        ctx.lineTo(x, y + h * 0.7);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        let cx = x + w / 2, cy = y + h * 0.44;
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 3, cy - 12, 6, 24);
        ctx.fillRect(cx - 12, cy - 3, 24, 6);
        ctx.restore();
    }
'''

# Insert badge fallback before function draw()
content = content.replace('    function draw() {', badge_fallback + '\n    function draw() {')

old_hud_perks = '''        // Perks
        let px = 25, py = canvas.height - 65;
        const perkColors = {'SPEED': '#f1c40f', 'FIRERATE': '#2ecc71', 'JUGGERNAUT': '#e74c3c', '3GUNS': '#9b59b6'};
        for (let p in player.perks) {
            if (player.perks[p]) {
                ctx.fillStyle = perkColors[p];
                ctx.fillRect(px, py, 42, 42);
                ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.strokeRect(px, py, 42, 42);
                px += 52;
            }
        }'''

new_hud_perks = '''        // Perks
        let px = 25, py = canvas.height - 65;
        const perkColors = {'SPEED': '#f1c40f', 'FIRERATE': '#2ecc71', 'JUGGERNAUT': '#e74c3c', '3GUNS': '#9b59b6'};
        for (let p in player.perks) {
            if (player.perks[p]) {
                if (p === 'JUGGERNAUT') {
                    // Ícone Juggernaut da Terceira Imagem com fundo preto removido & brilho dinâmico
                    ctx.save();
                    let bounce = (player.juggernautJustAcquiredTimer > 0) ? (1 + Math.sin(player.juggernautJustAcquiredTimer * 10) * 0.15) : 1.0;
                    let bSize = 46 * bounce;
                    let ox = (bSize - 46) / 2;
                    let oy = (bSize - 46) / 2;

                    ctx.shadowColor = 'rgba(239, 68, 68, 0.95)';
                    ctx.shadowBlur = (player.juggernautJustAcquiredTimer > 0) ? 22 : 14;

                    if (IMAGE_ASSETS.juggernaut_perk && IMAGE_ASSETS.juggernaut_perk.complete && IMAGE_ASSETS.juggernaut_perk.naturalWidth > 0) {
                        ctx.drawImage(IMAGE_ASSETS.juggernaut_perk, px - ox, py - 4 - oy, bSize, bSize);
                    } else {
                        drawJuggernautBadgeProcedural(ctx, px - ox, py - 4 - oy, bSize, bSize);
                    }
                    ctx.restore();
                    px += 54;
                } else {
                    ctx.fillStyle = perkColors[p];
                    ctx.fillRect(px, py, 42, 42);
                    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.strokeRect(px, py, 42, 42);
                    ctx.fillStyle = '#000000';
                    ctx.font = 'bold 9px "Press Start 2P", monospace';
                    ctx.textAlign = 'center';
                    let label = p === 'SPEED' ? 'SPD' : (p === 'FIRERATE' ? '2TAP' : 'MULE');
                    ctx.fillText(label, px + 21, py + 26);
                    px += 52;
                }
            }
        }'''

content = content.replace(old_hud_perks, new_hud_perks)

# 14. CHEAT CODE UPDATE
content = content.replace('Todas as colas (Double Tap, Speed Cola, Juggernog, Mule Kick)', 'Todas as colas (Double Tap, Speed Cola, Juggernaut, Mule Kick)')
old_cheat_jugg = '''        player.perks['SPEED'] = true;
        player.perks['FIRERATE'] = true;
        player.perks['JUGGERNAUT'] = true;
        player.perks['3GUNS'] = true;'''

new_cheat_jugg = '''        player.perks['SPEED'] = true;
        player.perks['FIRERATE'] = true;
        player.perks['JUGGERNAUT'] = true;
        player.perks['3GUNS'] = true;
        player.maxHealth = 200;
        player.health = 200;'''

content = content.replace(old_cheat_jugg, new_cheat_jugg)

# Write to code.html
with open('code.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully updated code.html with all Juggernaut features!')

# Atualização adicional: Garrafa de vidro, frames de animação, braços de robô e cheat GMMONEY
import subprocess
import sys
subprocess.run([sys.executable, 'update_game_assets_and_animation.py'], check=True)


/* ===== MERVE CAFE — three-scene.js — Cinematic 3D Hero ===== */
(function () {
  if (typeof THREE === 'undefined') return;

  const container = document.getElementById('hero-canvas');
  if (!container) return;

  /* ── Scene ── */
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x060402, 0.028);
  scene.background = new THREE.Color(0x060402);

  /* ── Camera ── */
  const camera = new THREE.PerspectiveCamera(
    70,
    window.innerWidth / window.innerHeight,
    0.1,
    200
  );
  camera.position.set(0, 0, 14);

  /* ── Renderer ── */
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  /* ── Lights ── */
  const ambient = new THREE.AmbientLight(0x1a0d05, 1.2);
  scene.add(ambient);

  const goldenLight = new THREE.PointLight(0xc9a96e, 8, 25);
  goldenLight.position.set(0, 0, 2);
  scene.add(goldenLight);

  const rimLight1 = new THREE.PointLight(0xff7722, 4, 18);
  rimLight1.position.set(-6, 4, -2);
  scene.add(rimLight1);

  const rimLight2 = new THREE.PointLight(0x8b4510, 3, 14);
  rimLight2.position.set(6, -3, 3);
  scene.add(rimLight2);

  const backLight = new THREE.PointLight(0xc9a96e, 2, 30);
  backLight.position.set(0, 8, -10);
  scene.add(backLight);

  /* ── Central Torus Knot (signature object) ── */
  const knotGeo = new THREE.TorusKnotGeometry(2, 0.55, 180, 32, 2, 3);
  const knotMat = new THREE.MeshStandardMaterial({
    color: 0xc9a96e,
    metalness: 0.95,
    roughness: 0.08,
    emissive: 0x3a1f08,
    emissiveIntensity: 0.4,
  });
  const knot = new THREE.Mesh(knotGeo, knotMat);
  scene.add(knot);

  /* ── Inner glow sphere ── */
  const glowGeo = new THREE.SphereGeometry(0.9, 32, 32);
  const glowMat = new THREE.MeshStandardMaterial({
    color: 0xffcc66,
    emissive: 0xdd8800,
    emissiveIntensity: 2.5,
    transparent: true,
    opacity: 0.85,
  });
  const glowSphere = new THREE.Mesh(glowGeo, glowMat);
  scene.add(glowSphere);

  /* ── Orbiting rings ── */
  const rings = [];
  const ringData = [
    { radius: 3.5, tube: 0.015, color: 0xc9a96e, opacity: 0.25, rx: 1.2, ry: 0.3, speed: 0.4 },
    { radius: 5.0, tube: 0.012, color: 0xc9a96e, opacity: 0.15, rx: 0.5, ry: 1.1, speed: -0.25 },
    { radius: 7.0, tube: 0.008, color: 0x8a6030, opacity: 0.1,  rx: 0.8, ry: 0.6, speed: 0.15 },
    { radius: 9.5, tube: 0.006, color: 0x8a6030, opacity: 0.06, rx: 0.2, ry: 0.9, speed: -0.1 },
  ];
  ringData.forEach(d => {
    const geo = new THREE.TorusGeometry(d.radius, d.tube, 12, 120);
    const mat = new THREE.MeshBasicMaterial({
      color: d.color,
      transparent: true,
      opacity: d.opacity,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.x = d.rx;
    mesh.rotation.y = d.ry;
    mesh.userData.speed = d.speed;
    scene.add(mesh);
    rings.push(mesh);
  });

  /* ── Coffee Bean Particles ── */
  const PARTICLE_COUNT = 900;
  const positions = new Float32Array(PARTICLE_COUNT * 3);
  const velocities = [];
  const sizes = new Float32Array(PARTICLE_COUNT);

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const r = 5 + Math.random() * 25;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);
    velocities.push({
      x: (Math.random() - 0.5) * 0.006,
      y: (Math.random() - 0.5) * 0.006 + 0.002,
      z: (Math.random() - 0.5) * 0.006,
    });
    sizes[i] = Math.random() * 2.5 + 0.5;
  }

  const particleGeo = new THREE.BufferGeometry();
  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  const particleMat = new THREE.PointsMaterial({
    color: 0xc9a96e,
    size: 0.07,
    transparent: true,
    opacity: 0.55,
    sizeAttenuation: true,
  });

  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  /* ── Steam Particles (rising) ── */
  const STEAM_COUNT = 200;
  const steamPos = new Float32Array(STEAM_COUNT * 3);
  const steamVel = [];
  for (let i = 0; i < STEAM_COUNT; i++) {
    steamPos[i * 3]     = (Math.random() - 0.5) * 4;
    steamPos[i * 3 + 1] = Math.random() * 10 - 5;
    steamPos[i * 3 + 2] = (Math.random() - 0.5) * 4;
    steamVel.push({
      x: (Math.random() - 0.5) * 0.003,
      y: 0.015 + Math.random() * 0.01,
      z: (Math.random() - 0.5) * 0.003,
      life: Math.random(),
    });
  }
  const steamGeo = new THREE.BufferGeometry();
  steamGeo.setAttribute('position', new THREE.BufferAttribute(steamPos, 3));
  const steamMat = new THREE.PointsMaterial({
    color: 0xf5e6c8,
    size: 0.04,
    transparent: true,
    opacity: 0.18,
    sizeAttenuation: true,
  });
  const steam = new THREE.Points(steamGeo, steamMat);
  scene.add(steam);

  /* ── Floating Geometric Accent Cubes ── */
  const accentObjs = [];
  const accentGeo = new THREE.OctahedronGeometry(0.15, 0);
  const accentMat = new THREE.MeshStandardMaterial({
    color: 0xc9a96e,
    metalness: 0.9,
    roughness: 0.1,
    emissive: 0x3a1f08,
    emissiveIntensity: 0.5,
  });

  for (let i = 0; i < 18; i++) {
    const mesh = new THREE.Mesh(accentGeo, accentMat);
    const angle = (i / 18) * Math.PI * 2;
    const rad = 4 + Math.random() * 3;
    mesh.position.set(
      Math.cos(angle) * rad,
      (Math.random() - 0.5) * 6,
      Math.sin(angle) * rad - 2
    );
    mesh.userData = { speed: 0.003 + Math.random() * 0.004, angle, rad, yOff: mesh.position.y };
    scene.add(mesh);
    accentObjs.push(mesh);
  }

  /* ── Mouse Parallax ── */
  let mouseX = 0, mouseY = 0;
  let targetCamX = 0, targetCamY = 0;

  document.addEventListener('mousemove', e => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  /* ── Clock ── */
  const clock = new THREE.Clock();

  /* ── Cinematic intro: camera zooms in ── */
  camera.position.z = 28;
  let introProgress = 0;
  const introDuration = 2.8;

  /* ── Animation Loop ── */
  function animate() {
    requestAnimationFrame(animate);
    const dt = clock.getDelta();
    const elapsed = clock.getElapsedTime();

    /* Intro zoom */
    if (introProgress < 1) {
      introProgress = Math.min(introProgress + dt / introDuration, 1);
      const ease = 1 - Math.pow(1 - introProgress, 3);
      camera.position.z = 28 - 14 * ease;
    }

    /* Torus knot rotation */
    knot.rotation.x = elapsed * 0.25;
    knot.rotation.y = elapsed * 0.18;
    knot.rotation.z = elapsed * 0.08;

    /* Glow sphere pulse */
    const pulse = 1 + Math.sin(elapsed * 2.5) * 0.12;
    glowSphere.scale.setScalar(pulse);
    goldenLight.intensity = 7 + Math.sin(elapsed * 3) * 1.5;
    glowMat.emissiveIntensity = 2 + Math.sin(elapsed * 2.5) * 0.7;

    /* Rings orbit */
    rings.forEach((ring, i) => {
      ring.rotation.z += ringData[i].speed * dt;
      ring.rotation.x += ringData[i].speed * 0.5 * dt;
    });

    /* Floating accent pieces */
    accentObjs.forEach(obj => {
      obj.userData.angle += obj.userData.speed;
      obj.position.x = Math.cos(obj.userData.angle) * obj.userData.rad;
      obj.position.z = Math.sin(obj.userData.angle) * obj.userData.rad - 2;
      obj.position.y = obj.userData.yOff + Math.sin(elapsed * 0.8 + obj.userData.angle) * 0.8;
      obj.rotation.x += 0.01;
      obj.rotation.y += 0.015;
    });

    /* Particle drift */
    const pos = particleGeo.attributes.position.array;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      pos[i*3]     += velocities[i].x;
      pos[i*3 + 1] += velocities[i].y;
      pos[i*3 + 2] += velocities[i].z;
      const dist = Math.sqrt(pos[i*3]**2 + pos[i*3+1]**2 + pos[i*3+2]**2);
      if (dist > 30) {
        pos[i*3]     *= 0.1;
        pos[i*3 + 1] *= 0.1;
        pos[i*3 + 2] *= 0.1;
      }
    }
    particleGeo.attributes.position.needsUpdate = true;
    particles.rotation.y = elapsed * 0.018;
    particles.rotation.x = elapsed * 0.007;

    /* Steam drift */
    const spos = steamGeo.attributes.position.array;
    for (let i = 0; i < STEAM_COUNT; i++) {
      spos[i*3]     += steamVel[i].x;
      spos[i*3 + 1] += steamVel[i].y;
      spos[i*3 + 2] += steamVel[i].z;
      if (spos[i*3+1] > 8) {
        spos[i*3]     = (Math.random()-0.5)*4;
        spos[i*3 + 1] = -5;
        spos[i*3 + 2] = (Math.random()-0.5)*4;
      }
    }
    steamGeo.attributes.position.needsUpdate = true;

    /* Mouse parallax — smooth lerp */
    targetCamX += (mouseX * 2.5 - targetCamX) * 0.04;
    targetCamY += (-mouseY * 1.5 - targetCamY) * 0.04;
    camera.position.x = targetCamX;
    camera.position.y = targetCamY;
    camera.lookAt(0, 0, 0);

    /* Light follows mouse slightly */
    goldenLight.position.x = mouseX * 3;
    goldenLight.position.y = -mouseY * 2;

    renderer.render(scene, camera);
  }

  animate();

  /* ── Resize ── */
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

})();

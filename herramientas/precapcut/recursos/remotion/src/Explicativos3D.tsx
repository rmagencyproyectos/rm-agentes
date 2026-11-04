import React, {useMemo} from 'react';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import * as THREE from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {RoundedBoxGeometry} from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import type {Props} from './Plantillas';

// Recursos explicativos en 3D (Three.js): objetos con volumen, luz de estudio y materiales reales
// (madera, mármol, lacado). Sin texto. Fondo transparente; cada uno ocupa un lienzo de TAM x TAM.
const TAM = 500;
const ROJO = '#c8463c';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const suave = Easing.bezier(0.16, 1, 0.3, 1);
const tramo = (s: number, a: number, b: number) => interpolate(s, [a, b], [0, 1], {...clamp, easing: suave});

const useT = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return {f, fps, s: f / fps};
};

// ---------------------------------------------------------------- escena común

const Entorno: React.FC = () => {
	const {gl, scene} = useThree();
	useMemo(() => {
		const pm = new THREE.PMREMGenerator(gl);
		scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
		scene.environmentIntensity = 0.55;
	}, [gl, scene]);
	return null;
};

const Mirar: React.FC<{a: [number, number, number]}> = ({a}) => {
	const {camera} = useThree();
	camera.lookAt(...a);
	return null;
};

const Escena: React.FC<{children: React.ReactNode; cam: [number, number, number]; mira?: [number, number, number]; fov?: number}> = ({children, cam, mira = [0, 0, 0], fov = 30}) => (
	<ThreeCanvas width={TAM} height={TAM} camera={{position: cam, fov}} gl={{antialias: true, alpha: true, preserveDrawingBuffer: true, toneMapping: THREE.NeutralToneMapping}}
		style={{filter: 'drop-shadow(0 22px 28px rgba(0,0,0,0.5))'}}>
		<Entorno />
		<Mirar a={mira} />
		<ambientLight intensity={0.15} />
		<directionalLight position={[3, 5, 4]} intensity={1.5} />
		<directionalLight position={[-4, 2, -3]} intensity={0.9} />
		{children}
	</ThreeCanvas>
);

// ---------------------------------------------------------------- texturas (deterministas)

const azar = (semilla: number) => () => {
	semilla = (semilla * 16807) % 2147483647;
	return semilla / 2147483647;
};

const useTextura = (clave: string, pintar: (c: CanvasRenderingContext2D, w: number, h: number) => void, w = 512, h = 512) =>
	useMemo(() => {
		const lienzo = document.createElement('canvas');
		lienzo.width = w;
		lienzo.height = h;
		pintar(lienzo.getContext('2d')!, w, h);
		const t = new THREE.CanvasTexture(lienzo);
		t.colorSpace = THREE.SRGBColorSpace;
		t.anisotropy = 8;
		return t;
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [clave]);

const pintarMadera = (base: string) => (c: CanvasRenderingContext2D, w: number, h: number) => {
	const r = azar(7);
	c.fillStyle = base;
	c.fillRect(0, 0, w, h);
	for (let i = 0; i < 90; i++) {
		const x0 = r() * w;
		c.strokeStyle = `rgba(${r() > 0.5 ? '40,22,10' : '255,230,200'},${0.05 + r() * 0.18})`;
		c.lineWidth = 1 + r() * 4;
		c.beginPath();
		for (let y = 0; y <= h; y += 16) c.lineTo(x0 + Math.sin(y / (40 + r() * 30) + i) * 10, y);
		c.stroke();
	}
};

const pintarMarmol = (c: CanvasRenderingContext2D, w: number, h: number) => {
	const r = azar(11);
	c.fillStyle = '#f3f0eb';
	c.fillRect(0, 0, w, h);
	c.filter = 'blur(1.2px)';
	for (let i = 0; i < 9; i++) {
		c.strokeStyle = `rgba(110,110,118,${0.2 + r() * 0.35})`;
		c.lineWidth = 1 + r() * 3;
		c.beginPath();
		c.moveTo(r() * w, 0);
		c.bezierCurveTo(r() * w, h * 0.3, r() * w, h * 0.7, r() * w, h);
		c.stroke();
	}
	c.filter = 'none';
};

const Caja: React.FC<{tam: [number, number, number]; radio?: number; children: React.ReactNode} & JSX.IntrinsicElements['mesh']> = ({tam, radio = 0.05, children, ...rest}) => {
	const geo = useMemo(() => new RoundedBoxGeometry(tam[0], tam[1], tam[2], 4, radio), [tam[0], tam[1], tam[2], radio]);
	return <mesh geometry={geo} {...rest}>{children}</mesh>;
};

// ---------------------------------------------------------------- 1) «materiales delicados»
// Encimera de mármol pulido; pasa un brillo y una raya roja la cruza levantando esquirlas.
export const Rayado3D: React.FC<{p: Props}> = () => {
	const {s} = useT();
	const marmol = useTextura('marmol', pintarMarmol);
	const curva = useMemo(() => new THREE.CatmullRomCurve3([
		new THREE.Vector3(-1.2, 0.151, -0.45), new THREE.Vector3(-0.4, 0.151, 0.05), new THREE.Vector3(0.3, 0.151, -0.1), new THREE.Vector3(1.15, 0.151, 0.45),
	]), []);
	const tubo = useMemo(() => new THREE.TubeGeometry(curva, 64, 0.028, 8), [curva]);
	const raya = tramo(s, 0.25, 0.8);
	tubo.setDrawRange(0, Math.floor(raya * 64) * 8 * 6);
	const punta = curva.getPoint(Math.max(0.001, raya));
	return (
		<Escena cam={[0, 4.2, 5.8]}>
			<group rotation={[0, -0.45 + 0.3 * tramo(s, 0, 1.4), 0]}>
				<Caja tam={[3.2, 0.3, 1.8]} radio={0.06}>
					<meshPhysicalMaterial map={marmol} roughness={0.12} clearcoat={1} clearcoatRoughness={0.05} />
				</Caja>
				<mesh geometry={tubo}><meshStandardMaterial color={ROJO} emissive={ROJO} emissiveIntensity={0.15} roughness={0.6} /></mesh>
				{raya > 0 && raya < 1 && [0, 1, 2, 3, 4].map((i) => {
					const vida = (s * 7 + i * 0.2) % 1;
					return (
						<mesh key={i} position={[punta.x + Math.sin(i * 2.1) * 0.25 * vida, 0.17 + vida * 0.45, punta.z + Math.cos(i * 1.7) * 0.25 * vida]}
							rotation={[i + s * 6, i, 0]} scale={(1 - vida) * 0.06}>
							<boxGeometry /><meshStandardMaterial color="#e9e4dc" />
						</mesh>
					);
				})}
			</group>
			<pointLight position={[interpolate(s, [0, 1.3], [-3, 3], clamp), 1.2, 0.8]} intensity={6} distance={6} />
		</Escena>
	);
};

// ---------------------------------------------------------------- 2) «colores que cansan»
// Tres muestras de lacado muy vivo que pierden el color y el brillo hasta quedar grises y mates.
export const ColorCansa3D: React.FC<{p: Props}> = () => {
	const {s} = useT();
	const k = tramo(s, 0.35, 1.15);
	const gris = new THREE.Color('#8b8a86');
	return (
		<Escena cam={[0, 0.5, 6.2]}>
			<group rotation={[0, Math.sin(s * 1.5) * 0.15, 0]}>
				{['#ff6a1f', '#00c2b2', '#ffd400'].map((c, i) => (
					<Caja key={c} tam={[0.85, 1.7, 0.12]} radio={0.05}
						position={[(i - 1) * 0.95, Math.sin(s * 3 + i) * 0.05, (i === 1 ? 0.15 : 0)]} rotation={[0, (1 - i) * 0.35, (i - 1) * -0.06]}>
						<meshPhysicalMaterial color={new THREE.Color(c).lerp(gris, k)} roughness={0.15 + 0.6 * k} clearcoat={1 - k} />
					</Caja>
				))}
			</group>
		</Escena>
	);
};

// ---------------------------------------------------------------- 3) «no encajan con el resto de la casa»
// Casa con un hueco de puzle; llega una pieza con otra forma, choca, la casa tiembla y la pieza rebota.
const formaPieza = (sh: THREE.Shape | THREE.Path, x: number, y: number, l: number, lateral: boolean) => {
	const r = l * 0.18;
	sh.moveTo(x, y);
	sh.lineTo(x + l, y);
	if (lateral) {
		sh.lineTo(x + l, y + l / 2 - r);
		sh.absarc(x + l + r * 0.8, y + l / 2, r, -Math.PI * 0.75, Math.PI * 0.75, false);
	}
	sh.lineTo(x + l, y + l);
	sh.lineTo(x + l / 2 + r, y + l);
	sh.absarc(x + l / 2, y + l + r * 0.8, r, -Math.PI * 0.25, Math.PI * 1.25, false);
	sh.lineTo(x, y + l);
	sh.lineTo(x, y);
};

export const Puzle3D: React.FC<{p: Props}> = ({p}) => {
	const {s, f, fps} = useT();
	const madera = useTextura('madera-casa', pintarMadera(p.color));
	const [casa, pieza] = useMemo(() => {
		const c = new THREE.Shape([new THREE.Vector2(-1.2, -1), new THREE.Vector2(1.2, -1), new THREE.Vector2(1.2, 0.35), new THREE.Vector2(0, 1.35), new THREE.Vector2(-1.2, 0.35)]);
		const hueco = new THREE.Path();
		formaPieza(hueco, -0.35, -0.55, 0.7, false);
		c.holes.push(hueco);
		const pz = new THREE.Shape();
		formaPieza(pz, -0.35, -0.35, 0.7, true);
		const ext = {depth: 0.35, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.03, bevelSegments: 3};
		const gc = new THREE.ExtrudeGeometry(c, ext);
		gc.translate(0, 0, -0.175);
		const gp = new THREE.ExtrudeGeometry(pz, ext);
		gp.translate(0, 0, -0.175);
		return [gc, gp];
	}, []);
	madera.wrapS = madera.wrapT = THREE.RepeatWrapping;
	madera.repeat.set(0.4, 0.4);
	const choque = 0.7;
	const ida = tramo(s, 0.1, choque);
	const rebote = spring({frame: f - choque * fps, fps, config: {damping: 9, stiffness: 120}});
	const tiembla = s > choque ? Math.sin((s - choque) * 40) * 0.05 * Math.exp(-(s - choque) * 5) : 0;
	return (
		<Escena cam={[0.95, 0.5, 6.8]} mira={[0.75, 0, 0]}>
			<group rotation={[0, -0.35, tiembla]}>
				<mesh geometry={casa}><meshPhysicalMaterial map={madera} roughness={0.35} clearcoat={0.6} /></mesh>
				<mesh geometry={pieza}
					position={[interpolate(ida, [0, 1], [3.4, 0.05]) + rebote * 1.2, -0.2 - rebote * 0.35, interpolate(ida, [0, 1], [1.4, 0.45]) + rebote * 0.7]}
					rotation={[rebote * 0.3, -0.3 + ida * 0.3 + rebote * 0.4, -rebote * 0.6]}>
					<meshPhysicalMaterial color={ROJO} roughness={0.25} clearcoat={1} />
				</mesh>
			</group>
		</Escena>
	);
};

// ---------------------------------------------------------------- 4) «comparar texturas, colores y acabados»
// Muestrario real (madera, mármol, lacado de la marca) que se abre en abanico sobre su tornillo.
export const Muestrario3D: React.FC<{p: Props}> = ({p}) => {
	const {s, f, fps} = useT();
	const madera = useTextura('madera', pintarMadera('#8a5a33'));
	const marmol = useTextura('marmol', pintarMarmol);
	const geo = useMemo(() => {
		const g = new RoundedBoxGeometry(0.9, 2.1, 0.07, 4, 0.04);
		g.translate(0, 0.9, 0);
		return g;
	}, []);
	const mats = [
		<meshPhysicalMaterial key="m" map={madera} roughness={0.55} />,
		<meshPhysicalMaterial key="r" map={marmol} roughness={0.1} clearcoat={1} />,
		<meshPhysicalMaterial key="l" color={p.color} roughness={0.2} clearcoat={1} clearcoatRoughness={0.05} />,
	];
	return (
		<Escena cam={[0, 1.2, 5.6]} mira={[0, 0.8, 0]}>
			<group rotation={[-0.1, -0.35 + 0.25 * tramo(s, 0, 2.4), 0]}>
				{mats.map((m, i) => {
					const v = spring({frame: f - i * 0.18 * fps, fps, config: {damping: 11, stiffness: 110}});
					return <mesh key={i} geometry={geo} position={[0, 0, i * 0.08]} rotation={[0, 0, (1 - i) * 0.5 * v]}>{m}</mesh>;
				})}
				<mesh position={[0, 0, 0.12]} rotation={[Math.PI / 2, 0, 0]}>
					<cylinderGeometry args={[0.07, 0.07, 0.34, 24]} />
					<meshStandardMaterial color="#d8d8d8" metalness={1} roughness={0.2} />
				</mesh>
			</group>
		</Escena>
	);
};

// ---------------------------------------------------------------- 5) «verlo en una foto que verlo delante tuyo»
// Móvil con la cocina dibujada en plano; el mueble sale de la pantalla con volumen y gira para enseñar su fondo.
export const MovilFoto3D: React.FC<{p: Props}> = ({p}) => {
	const {f, fps} = useT();
	const foto = useTextura('foto-' + p.color, (c, w, h) => {
		c.fillStyle = '#dcdad6';
		c.fillRect(0, 0, w, h);
		c.fillStyle = '#f6f5f2';
		c.fillRect(w * 0.1, h * 0.42, w * 0.8, h * 0.05);
		c.fillStyle = p.color;
		c.fillRect(w * 0.12, h * 0.47, w * 0.76, h * 0.2);
		c.strokeStyle = 'rgba(255,255,255,0.7)';
		c.lineWidth = 4;
		[0.37, 0.62].forEach((x) => {
			c.beginPath();
			c.moveTo(w * x, h * 0.47);
			c.lineTo(w * x, h * 0.67);
			c.stroke();
		});
	}, 256, 512);
	const madera = useTextura('madera-mueble', pintarMadera(p.color));
	const marmol = useTextura('marmol', pintarMarmol);
	const sale = spring({frame: f - 0.5 * fps, fps, config: {damping: 13, stiffness: 90}});
	return (
		<Escena cam={[0.4, 0.4, 5.4]} mira={[0.2, 0, 0.4]}>
			<group rotation={[0, 0.35 - 0.2 * sale, 0]}>
				<Caja tam={[1.05, 2.1, 0.1]} radio={0.045}><meshPhysicalMaterial color="#111" metalness={0.4} roughness={0.25} clearcoat={1} /></Caja>
				<mesh position={[0, 0, 0.052]}>
					<planeGeometry args={[0.95, 1.95]} />
					<meshBasicMaterial map={foto} color={new THREE.Color('#ffffff').lerp(new THREE.Color('#333'), sale * 0.7)} toneMapped={false} />
				</mesh>
				<group position={[0.15 * sale, -0.05 + 0.15 * sale, 0.1 + 1.1 * sale]} scale={0.25 + 0.75 * sale} rotation={[0.15 * sale, -0.7 * sale, 0]}>
					<Caja tam={[1.5, 0.8, 0.65]} radio={0.03}><meshPhysicalMaterial map={madera} roughness={0.4} clearcoat={0.5} /></Caja>
					{[-0.25, 0.25].map((x) => (
						<mesh key={x} position={[x, 0, 0.33]}><boxGeometry args={[0.012, 0.72, 0.01]} /><meshStandardMaterial color="#2b1a10" /></mesh>
					))}
					<Caja tam={[1.6, 0.08, 0.72]} radio={0.02} position={[0, 0.44, 0.02]}><meshPhysicalMaterial map={marmol} roughness={0.1} clearcoat={1} /></Caja>
				</group>
			</group>
		</Escena>
	);
};

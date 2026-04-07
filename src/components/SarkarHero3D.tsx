'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Text, Float } from '@react-three/drei';
import { useRef, useMemo } from 'react';
import * as THREE from 'three';

function SarkarText() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.15) * 0.12;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.04;
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.15;
    }
  });

  return (
    <Float speed={1.2} rotationIntensity={0.08} floatIntensity={0.2}>
      <group ref={groupRef}>
        {/* Main glowing text */}
        <Text
          fontSize={3}
          fontWeight={900}
          letterSpacing={0.15}
          color="#7c3aed"
          anchorX="center"
          anchorY="middle"
          material-transparent={true}
          material-opacity={0.25}
        >
          SARKAR
          <meshStandardMaterial
            color="#7c3aed"
            emissive="#7c3aed"
            emissiveIntensity={0.6}
            transparent
            opacity={0.25}
            metalness={0.9}
            roughness={0.1}
          />
        </Text>
        {/* Glow layer */}
        <Text
          fontSize={3}
          fontWeight={900}
          letterSpacing={0.15}
          anchorX="center"
          anchorY="middle"
          position={[0, 0, -0.1]}
        >
          SARKAR
          <meshBasicMaterial
            color="#a78bfa"
            transparent
            opacity={0.08}
          />
        </Text>
      </group>
    </Float>
  );
}

function FloatingParticles() {
  const points = useRef<THREE.Points>(null);
  const count = 250;

  const [positions, sizes] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const sz = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 25;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 15;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 15;
      sz[i] = Math.random() * 0.04 + 0.01;
    }
    return [pos, sz];
  }, []);

  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y = state.clock.elapsedTime * 0.015;
      points.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.08) * 0.02;
    }
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-size" args={[sizes, 1]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.04}
        color="#8b5cf6"
        transparent
        opacity={0.5}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

function GlowRings() {
  const ring1 = useRef<THREE.Mesh>(null);
  const ring2 = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (ring1.current) {
      ring1.current.rotation.x = t * 0.1;
      ring1.current.rotation.z = t * 0.05;
    }
    if (ring2.current) {
      ring2.current.rotation.y = t * 0.08;
      ring2.current.rotation.z = -t * 0.04;
    }
  });

  return (
    <>
      <mesh ref={ring1} position={[0, 0, -1]}>
        <torusGeometry args={[4.5, 0.015, 16, 100]} />
        <meshBasicMaterial color="#7c3aed" transparent opacity={0.12} />
      </mesh>
      <mesh ref={ring2} position={[0, 0, -1]}>
        <torusGeometry args={[5.5, 0.01, 16, 100]} />
        <meshBasicMaterial color="#0ea5e9" transparent opacity={0.08} />
      </mesh>
    </>
  );
}

export default function SarkarHero3D() {
  return (
    <div className="absolute inset-0 z-0" style={{ filter: 'blur(1px)' }}>
      <Canvas
        camera={{ position: [0, 0, 10], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
        dpr={[1, 1.5]}
      >
        <ambientLight intensity={0.2} />
        <directionalLight position={[5, 5, 5]} intensity={0.6} color="#a78bfa" />
        <directionalLight position={[-5, -3, 3]} intensity={0.3} color="#0ea5e9" />
        <pointLight position={[0, 0, 5]} intensity={0.8} color="#7c3aed" distance={12} />
        <pointLight position={[3, 2, 4]} intensity={0.3} color="#0ea5e9" distance={8} />
        <SarkarText />
        <FloatingParticles />
        <GlowRings />
      </Canvas>
    </div>
  );
}

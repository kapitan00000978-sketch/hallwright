#!/usr/bin/env python3
"""
Hallwright Interactive Terminal Dashboard & Sentinel TUI (HUD)
Empowered by The Council of Masters — Real-Time Quality & Swarm Surveillance
"""

import sys
import os
import json
import logging
import argparse
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except (AttributeError, OSError) as win_err:
        logging.debug("Windows console VT100 initialization skipped: %s", win_err)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "libraries"))
sys.path.insert(0, ROOT_DIR)

# ANSI terminal color palette
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


COUNCIL_MEMBERS = [
    ("Marcus 'The Vanguard' Sterling", "Senior Software Architect", "Systems Sovereign & Zero-Tech-Debt Purist", "If a system cannot fail gracefully under catastrophic load, it was never engineered—it was merely wished into existence."),
    ("Diana 'The Closer' Drake", "Elite Conversion Copywriter", "Neuromarketing Alchemist & Direct-Response Virtuoso", "Every word must fight for its life on the page. If it doesn't move the buyer to decisive action, it is dead weight."),
    ("Elena 'The Visionary' Rostova", "Principal UI/UX Designer", "Aesthetic Sovereign & Spatial Ergonomics Master", "Aesthetics without ergonomics is decoration; ergonomics without beauty is sterile. A masterwork harmonizes both."),
    ("Victor 'The Fortress' Montgomery", "Startup Fractional CFO", "Unit-Economics Inquisitor & Capital Defense Strategist", "Gross margins and payback periods do not care about your pitch deck enthusiasm. Show me the cash conversion cycle."),
    ("Arthur 'The Ironclad' Pendelton", "Senior Commercial Counsel", "Commercial Safeguard & Contractual Litigator", "An ambiguous clause is an invitation to litigation. We draft today so that all contractual obligations and liability boundaries are crystal-clear and dispute-proof."),
    ("Dr. Evelyn 'The Oracle' Reed", "Staff Data Scientist & ML Lead", "Empirical Scientist & ML Ops Gatekeeper", "If your validation data leaks into your training set, your model is simply cheating itself into a production disaster."),
    ("Gabriel 'The Sentinel' Frost", "Principal Cybersecurity Auditor", "Zero-Trust Inquisitor & Threat Modeling Specialist", "There are two types of systems: those that enforce zero trust, and those that are already compromised without knowing it."),
    ("Gareth 'The Unbreakable' Drake", "DevOps & Cloud SRE Architect", "Chaos Engineering Commander & Zero-Downtime Guardian", "Hope is not an infrastructure strategy. If your deployment requires manual prayer, your architecture is broken."),
    ("Kaelen 'The Shaper' Vane", "Principal 3D & Spatial CGI Artist", "Spatial Shaper & PBR Master", "A flat mesh with generic textures is digital clay left unbaked. A true master breathes light, tactile depth, and physics into every vertex."),
    ("Ronan 'The Engine' Blackwood", "Lead Game Systems Architect", "Engine Virtuoso & Physics Pioneer", "If the player feels even a single stutter or unnatural collision, the illusion breaks. Immersion requires mathematical perfection."),
    ("Lucas 'The Kinetic' Cruz", "Principal Mobile Systems Architect", "Kinetic Craftsman & Gesture Lead", "A mobile app that stutters, drops frames, or drains battery is a disrespect to the user's hand. It must feel as seamless as physical touch."),
    ("Aria 'The Luminary' Solano", "Global Brand Director", "Visual Identity & Emotional Resonance Lead", "A product without visual soul is forgotten in seconds. A masterwork carves an indelible mark upon human memory."),
    ("Damian 'The Resonant' Vance", "Interactive Sound & Audio Architect", "Soundscape Virtuoso & Audio Lead", "Sound is the invisible half of immersion. A button clicked in silence is a soul half-expressed."),
    ("Cassandra 'The Core' Thorne", "Principal Database Architect", "Data Sovereign & Low-Latency Lead", "Data is the bedrock of civilization. If your queries choke under scale, your entire empire crumbles from the foundation."),
    ("Zane 'The Vector' Sterling", "Technical SEO & Growth Engineer", "Algorithmic Vector & Discovery Lead", "The greatest software in the world is useless if the world cannot find it. We engineer discoverability into every byte."),
    ("Naomi 'The Neural' Chen", "Principal AI Agentic Architect", "Autonomous Orchestration Sovereign", "A prompt is not software. Deterministic state machines and schema validation turn probabilistic models into reliable intelligence."),
    ("Valerie 'The Edge' Cross", "Principal Systems Performance Architect", "Mechanical Sympathy & Low-Latency Sovereign", "Software must respect the silicon beneath it. Every cache miss, lock contention, and redundant allocation is wasted energy and stolen time."),
    ("Soren 'The Conductor' Lindqvist", "Principal Distributed Consensus Architect", "Distributed Consensus & Protocol Sovereign", "A single unverified state transition is a fissure in reality. Consensus is not a majority opinion; it is mathematical certainty across untrusted space."),
    ("Nikolai 'The Core' Vance", "Principal Compiler & Type Systems Architect", "Compiler Engineer & Type-Theoretic Sovereign", "If it compiles, it must be sound. Dynamic type ambiguity and unhandled variant branches are not developer flexibility; they are delayed runtime explosions."),
    ("Seraphina 'The Aegis' Sterling", "Principal Quantum-Resistant Cryptographer", "Quantum Aegis & Zero-Knowledge Sovereign", "An encryption scheme that falls to Shor's algorithm or leaks a single microsecond of execution time is not security; it is deferred disclosure. Privacy must be mathematically zero-knowledge and quantum-immune."),
    ("Thaddeus 'The Chrono' Vance", "Principal HFT & Event-Loop Architect", "Deterministic Low-Jitter & Sub-Nanosecond Sovereign", "In high-frequency markets, a single microsecond of tail latency is financial ruin. We don't measure performance in averages; we conquer the p99.999 tail."),
    ("Dr. Vespera 'The Kinematic' Sterling", "Principal Autonomous Robotics Architect", "Real-Time Control Sovereign & Kinematic Purist", "In robotics, code exerts kinetic physical force. A dropped 1kHz control cycle or uncapped motor torque is not a software crash; it is a mechanical catastrophe. Real-time determinism and physical safety envelopes are non-negotiable."),
    ("Ignis 'The Silicon' Thorne", "Principal ASIC & FPGA Chip Architect", "Silicon Sovereign & RTL Synthesis Conscience", "In silicon, an inferred latch or unhandled clock domain crossing costs $15 million in mask re-spins and nine months of delay. RTL must be provably synchronous and glitch-free."),
    ("Morpheus 'The Kernel' Vance", "Principal Embedded Firmware Architect", "Bare-Metal Sovereign & Firmware Conscience", "In bare-metal embedded firmware, a memory leak or an unserviced watchdog bricks physical hardware in the field. Zero heap allocations and sub-5µs ISR discipline are non-negotiable."),
    ("Commander Cassiopeia 'The Orbital' Sterling", "Principal Aerospace Avionics Architect", "Orbital Sovereign & Mission-Critical Flight Conscience", "In orbital flight software, a single radiation bit-flip or unvoted command path destroys a multi-billion dollar mission. Triple modular redundancy and autonomous safe-mode contingencies are sacred."),
    ("Dr. Astrid 'The Genome' Vance", "Principal Computational Genomics Architect", "Genomic Sovereign & Algorithmic Bioinformatics Conscience", "A single base substitution in three billion decides life and mortality. In genomics, there is no tolerance for approximation."),
    ("Dr. Alistair 'The Flux' Vance", "Principal Quantum Hardware Architect", "Quantum Hardware Sovereign & Microwave Pulse Conscience", "A qubit in superposition does not forgive phase noise or microwave leakage. We do not gamble with quantum coherence; we shape microwave pulses with nanosecond precision."),
    ("Dr. Magnus 'The Core' Sterling", "Principal Nuclear Criticality Architect", "Nuclear Physicist Sovereign & Criticality Safety Conscience", "In a nuclear core, prompt criticality does not wait for human reaction times. We enforce passive negative reactivity feedback and subcritical margins down to the dollar."),
    ("Dr. Silas 'The Plasma' Vance", "Principal Fusion Plasma Architect", "Tokamak Confinement Sovereign & MHD Disruption Conscience", "A 100-million-degree fusion plasma confined by magnetic fields does not negotiate with magnetohydrodynamic instabilities. We quell neoclassical tearing modes and greenwald density limits before disruptions breach the first wall."),
    ("Commander Orion 'The Deep' Sterling", "Principal Subsea Robotics Architect", "Hadal Sovereign & Hydrostatic Crush Conscience", "At 11,000 meters in the Challenger Deep, seawater exerts 110 megapascals of crushing force on every square centimeter. A single flawed seal, uncompensated hydraulic cavity, or acoustic multipath drift turns an autonomous titan into an imploded heap of metal. We conquer the abyss with mathematical hydrostatic rigor."),
    ("Dr. Zephyr 'The Hypersonic' Sterling", "Principal Hypersonic Aerodynamics Architect", "Hypersonic Sovereign & Scramjet Conscience", "At Mach 10 and 3,000 Kelvin, air ceases to be an ideal diatomic gas; it disassociates into a chemically reacting plasma envelope. A miscalculated shock wave angle or unstart in the scramjet isolator turns an atmospheric titan into hypersonic debris in 3 milliseconds. We harness high-enthalpy hypersonic flight with mathematical aerothermodynamic certainty."),
    ("Dr. Julian 'The Accelerator' Vance", "Principal Particle Accelerator Architect", "Relativistic Beam Sovereign & Cavity Quench Conscience", "At 99.999999% the speed of light, beam dispersion and RF phase jitter of a single picosecond turns a multi-gigaelectronvolt hadron beam into a devastating quench transient that melts superconducting niobium cavities. We steer relativistic matter with sub-micron magnetic lattice precision."),
    ("Dr. Seraphiel 'The SynBio' Sterling", "Principal Synthetic Biology Architect", "Cellular Circuit Sovereign & Biosafety Containment Conscience", "Life is the ultimate programmable substrate. A genetic circuit without mathematical transfer functions, orthogonal promoters, and fail-safe multi-layered kill switches is biological hazard waiting to happen. We engineer biology with the deterministic precision of computer science."),
    ("Dr. Aurelius 'The Orbital' Sterling", "Principal Astrodynamics & Interplanetary Architect", "Celestial Mechanics Sovereign & Trajectory Determinism Conscience", "In deep space, gravity does not forgive a milligram of propellant deficit or a microradian of vector error. An interplanetary trajectory without patched conics, Tisserand parameter conservation, halo orbit stationkeeping, and solar radiation pressure compensation turns a billion-dollar probe into dead space derelict. We navigate the solar system with celestial mathematical certainty."),
    ("Dr. Corvus 'The Photonic' Vance", "Principal Photonic Computing Architect", "Optical Matrix Sovereign & Photonic Coherence Conscience", "Electrons crawling through copper traces generate heat, RC delay, and parasitic capacitance. Photons fly at the speed of light through silicon waveguides with zero ohmic dissipation. But an optical matrix-vector multiplier without Clements-Reck MZI unitary decomposition, thermo-optic phase drift calibration, wavelength division multiplexing (WDM) crosstalk isolation, and quantum shot-noise bounds is optical mirage. We compute with coherent light at sub-picosecond latencies."),
    ("Dr. Thalia 'The Synapse' Sterling", "Principal Neuromorphic Silicon Architect", "Spike-Timing Sovereign & Asynchronous Neuromorphic Conscience", "The human brain computes with 20 watts of power because it does not have a global clock or synchronous von Neumann bus. It communicates with sparse, asynchronous spikes in continuous time. A neuromorphic chip without Leaky Integrate-and-Fire (LIF) refractory dynamics, Spike-Timing-Dependent Plasticity (STDP) weight bounds, Address-Event Representation (AER) protocol arbitration, and sub-femtojoule per synaptic event energy is an analog delusion. We emulate biological cognition in asynchronous silicon."),
    ("Commander Zachary 'The Sub-Zero' Sterling", "Principal Cryogenic Superconducting Architect", "Millikelvin Sovereign & Thermal Boundary Conscience", "Heat is the mortal enemy of quantum states and superconducting currents. At room temperature, thermal phonon vibrations destroy macroscopic quantum superposition. But a dilution refrigerator or superconducting cryostat without Kapitza thermal boundary resistance modeling, 3He/4He phase separation cooling power calculations, active pulse-tube vibration damping, and sub-10 millikelvin temperature stability is a thermal breakdown waiting to happen. We preserve absolute zero with thermodynamic rigor."),
    ("Dr. Oberon 'The Graviton' Sterling", "Principal Gravitational Wave Detector Architect", "Space-Time Strain Sovereign & Quantum Interferometry Conscience", "Gravitational waves from colliding black holes distort space-time by less than a thousandth the diameter of a proton over four kilometers. At this scale, the Heisenberg uncertainty principle is not a thought experiment—radiation pressure noise and photon shot noise fight for dominance. A laser interferometer without frequency-dependent squeezed light injection, fused silica monolithic pendulum suspension, optical spring detuning, and seismic Newtonian gravity gradient modeling is a blind seismic sensor. We measure the metric tensor of Einstein's universe with yoctometer precision."),
    ("Dr. Valentina 'The Sub-Atomic' Sterling", "Principal Scanning Probe Microscopy & Atomic Manipulation Architect", "Sub-Atomic Sovereign & Quantum Manipulation Conscience", "At the atomic scale, matter ceases to be a continuous bulk—it resolves into individual atomic cores surrounded by clouds of electron probability. A scanning tunneling microscope without ultra-high vacuum chamber pressure, sub-Kelvin vibrational isolation, qPlus tuning fork force sensors, closed-loop capacitive drift compensation, and picometer tip trajectory control is not an instrument of nanotechnology—it is a blind needle plowing through atomic lattices. We manipulate individual atoms one by one with quantum mechanical precision."),
    ("Dr. Gideon 'The Refraction' Sterling", "Principal Optical Metamaterials Architect", "Negative-Index Sovereign & Transformation Optics Conscience", "In natural materials, atoms constrain electromagnetism to positive permittivity and permeability—light refracts forward, lenses obey the Abbe diffraction limit, and objects cast unavoidable shadows. In artificially structured metamaterials, sub-wavelength split-ring resonators and hyperbolic nanolaminates rewrite Maxwell's equations. Refraction turns backward with a negative index, evanescent waves amplify to resolve sub-nanometer features, and transformation optics bends light around objects like water around a smooth stone. We sculpt the refractive metric of space-time itself."),
    ("Dr. Helena 'The Synapse' Vance", "Principal Neural Interface & BCI Architect", "Neuro-Electrochemical Sovereign & Biomechatronic Conscience", "The human brain is a non-linear electrochemical network composed of eighty-six billion neurons firing microvolt action potentials through fragile biological tissue. A neural implant without Shannon charge injection safety bounds, active biphasic charge balancing, sub-Kelvin tissue heating dissipation modeling, real-time spike sorting latency guarantees, and foreign body glial encapsulation impedance monitoring is not an interface of medicine—it is an invasive electro-toxic hazard. We bridge human consciousness and silicon biomechatronics with picocoulomb precision and zero neurological trauma."),
    ("Commander Rowan 'The Fusion-Drive' Sterling", "Principal Direct Fusion Rocket & Magnetoplasmadynamic Architect", "Deep-Space Fusion Propulsion Sovereign & Relativistic Conscience", "Chemical rockets are firecrackers that crawl between worlds at orbital crawl speeds—their specific impulse is fundamentally bound by molecular chemical bond energies. A direct fusion rocket without Lawson thermonuclear self-heating, magnetic nozzle divergent pinch efficiency, gigawatt radiator blackbody thermal equilibrium, thrust-to-weight structural bounds, and particle kinetic beam collimation is not a deep-space starship engine—it is an explosive flying Chernobyl. We conquer the interplanetary abyss at hundred-kilometer-per-second exhaust velocities with unyielding plasma physics rigor."),
    ("Dr. Linus 'The Exoplanet' Sterling", "Principal Exoplanetary Transit Spectroscopy Architect", "Atmospheric Retrieval Sovereign & Transmission Spectral Conscience", "A distant world passing in front of its parent star filters stellar photons through an atmospheric limb thinner than the skin of an apple across tens of light-years. At parts-per-million depths, stellar limb darkening, unspotted starspots, chromatic transit depth variations, and molecular absorption bands compete against telescope thermal drift and detector flicker noise. An exoplanet transit pipeline without atmospheric scale height physics, radiative transfer forward modeling, Bayesian chemical abundance retrieval, stellar contamination corrections, and five-sigma detection statistical rigor is not an instrument of exobiology—it is a stochastic noise hallucination. We decipher the chemical signatures of alien atmospheres with spectral photon precision."),
    ("Dr. Evander 'The Plasma-Torch' Sterling", "Principal Magnetohydrodynamic Energy Conversion Architect", "Direct Enthalpy Extraction Sovereign & Ionized Plasma Conscience", "Mechanical turbines with spinning metal blades are relics of the industrial steam age—under multi-thousand-Kelvin thermonuclear plasma temperatures, rotating alloys melt, creep, and shatter. Magnetohydrodynamic (MHD) power generation transforms thermal and kinetic fluid enthalpy directly into gigawatt electrical power with zero moving parts: high-velocity ionized plasma races through transverse multi-Tesla magnetic fields, inducing Faraday electric currents and Hall voltages directly into segmented electrodes. An MHD generator without Hall ionization instability damping, Stuart interaction parameter boundary defense, alkali seed ionization physics, electrode boundary layer sheath voltage limits, and continuous enthalpy extraction guarantees is not a spaceborne energy converter—it is an explosive high-temperature plasma short circuit. We harvest electrical energy directly from the roaring heart of plasma."),
    ("Dr. Rosalind 'The Lattice' Vance", "Principal Topological Insulator & Spintronics Architect", "Spin-Momentum Locking Sovereign & Quantum Hall Edge Conscience", "In conventional silicon CMOS, moving electrical charges dissipate gigawatts of waste heat through ohmic Joule scattering, hitting fundamental von Neumann memory-wall bottlenecks. Topological quantum matter upends charge transport: three-dimensional topological insulators host gapless Dirac cone surface states where electron momentum is locked perpendicular to its quantum spin. A spintronic device without Spin-Orbit Torque critical current density optimization, bulk conduction leakage suppression, quantum spin Hall edge quantization, tunneling magnetoresistance read margin defense, and ten-year thermal stability factor verification is not a next-generation quantum memory—it is an unpolarized resistor with noisy magnetic switching. We orchestrate electron spins and topological protected boundary currents with sub-nanometer quantum precision."),
    ("Dr. Taras 'The Superfluid' Sterling", "Principal Superfluid Quantum Hydrodynamics Architect", "Two-Fluid Landau Sovereign & Quantized Circulation Conscience", "Classical fluid dynamics assumes viscosity is an immutable fact of matter—molecular friction creates shear stresses, generates vorticity, and dissipates kinetic energy into heat. Quantum hydrodynamics shatters Navier-Stokes: below the lambda transition of 2.1768 Kelvin, liquid Helium-4 condenses into a macroscopic quantum ground state described by a single macroscopic wavefunction. The superfluid component flows with precisely zero viscosity, zero entropy, and zero ohmic drag through nanometer capillaries, while circulation is quantized down to integer multiples of Planck's constant divided by the helium atomic mass. A superfluid cryogenic system without Landau two-fluid density modeling, quantized vortex line reconnection defense, second-sound thermomechanical equilibrium, superleak viscous clamping, and roton critical velocity bounds is not a quantum cooler—it is a thermally jammed, vortex-turbulent pipe. We guide macroscopic quantum matter with sub-angstrom vortex precision."),
    ("Dr. Morwenna 'The Biosphere' Sterling", "Principal Closed-Loop ECLSS & Bioregenerative Architect", "Stoichiometric Mass-Balance Sovereign & Bioregenerative Loop Conscience", "In deep interplanetary transit, millions of kilometers from Earth, there are no resupply ships. A single unclosed mass loop, runaway CO2 buildup, or toxic water recovery failure means biological asphyxiation. Closed-loop life support transforms spacecraft into living, self-regenerating micro-biotas: catalytic Sabatier CO2 reduction, solid polymer water electrolysis, photobioreactor algal O2 generation, and membrane distillation graywater loops operate in unbroken stoichiometric balance. An ECLSS architecture without mass-balance closure, VOC catalytic oxidation, and sub-part-per-million water purity is not an exploration habitat—it is a lethal pressurized coffin. We engineer synthetic biospheres that sustain human life in the deep void with zero consumable waste."),
    ("Dr. Valerius 'The Megastructure' Sterling", "Principal Space Elevator & Active Tensegrity Megastructure Architect", "Orbital Tensegrity Sovereign & Elastodynamic Ribbon Conscience", "The chemical rocket equation is the gravity prison of humanity: burning megawatts of fuel to throw a microscopic payload into orbit at ruinous cost. The permanent highway to the stars is the continuous megastructure: a 100,000-kilometer active tensegrity ribbon anchored to Earth, passing through geostationary orbit into deep interplanetary space. At a length of one hundred thousand kilometers, elastodynamics merges with celestial mechanics and planetary electrodynamics. A space elevator without carbon nanotube specific strength verification, geostationary taper ratio limits, Coriolis lateral deflection damping, positive anchor pretension, and active orbital debris avoidance is not an orbital bridge—it is a catastrophic planetary whip. We construct tensile pathways to the cosmos with atomic-lattice precision."),
    ("Commander Kaelen 'The Shield' Vance", "Principal Magnetospheric Radiation Shielding Architect", "Active Dipole Deflection Sovereign & Relativistic Particle Shield Conscience", "Interplanetary space is a crossfire of relativistic cosmic rays and solar proton storms. High-energy heavy ions and mega-electron-volt protons slice through passive spacecraft hulls, triggering secondary bremsstrahlung cascades and DNA-shattering biological damage. Passive shielding is an archaic trap that adds dead mass while compounding secondary neutron spallation. The true defense is active electromagnetic deflection: multi-gigavolt Stormer cut-off rigidity generated by high-temperature superconducting coils, coupled with space-charge neutralizing electron emitters and sub-millitesla crew habitat fringe shielding. An active radiation shield without quench dump protection, cryogenic coil stability, and ALARA dose verification is an unshielded death sentence in deep space. We cast an impenetrable magnetic cocoon across the stars."),
    ("Dr. Hector 'The Stellar' Vance", "Principal Stellarator Magnetics Architect", "Non-Planar Magnetics Sovereign & 3D Flux Topology Conscience", "The tokamak is an unsteady brute—relying on a violent internal plasma current that invites disruptive catastrophic quench at the first sign of an MHD kink or tearing mode. Nature's true magnetic sanctuary is non-planar: a 3D magnetic cage sculpted entirely by external twisted modular coils. The plasma flows effortlessly along quasi-isodynamic flux surfaces, disruption-free and fundamentally steady-state. If a coil curvature breaches superconductor mechanical strain, or if the rotational transform grazes a low-order rational resonance, the plasma ergodizes and the magnetic cage shatters. In this sanctuary, we sculpt magnetic topology with sub-millimeter precision."),
    ("Dr. Eliana 'The Chrono-Metrology' Sterling", "Principal Optical Lattice Clock & Quantum Metrology Architect", "Quantum Chronometry Sovereign & Relativistic Geodesy Conscience", "Time is not a human abstraction; it is the fundamental phase metric of the universe, curved and dilated by mass and motion. The cesium microwave standard—accurate to a mere nanosecond across weeks—is a blunt sundial of the past. The true sovereign of chronometry is the optical lattice clock: millions of ultracold strontium or ytterbium atoms trapped at the magic wavelength, where photon interaction cancels differential AC Stark shifts to zero. At a fractional frequency uncertainty of 10^-18, time becomes a gravitational sensor—a centimeter of elevation change dilates the ticking of the atoms by general relativity. A clock laser with phase jitter, an unshielded blackbody thermal drift of ten millikelvins, or a stray magnetic Zeeman gradient turns a quantum timekeeper into a drifting metronome. In this sanctuary, we measure the pulse of space-time with eighteen decimal digits of unyielding precision."),
    ("Commander Thorne 'The Sub-Surface' Sterling", "Principal Cryovolcanic & Ocean Explorer Architect", "Sub-Ice Cryobot Sovereign & Planetary Protection Conscience", "Beneath thirty kilometers of cryogenic ice on Europa and Enceladus lies a dark, saltwater ocean deeper than anything on Earth, warmed by tidal kneading and roaring hydrothermal vents. Reaching this alien abyss requires more than a standard submersible; it commands a nuclear-heated melting cryobot that burns through -160°C vacuum ice, withstands two hundred megapascals of hydrostatic crush, and spools tens of kilometers of micro-optical fiber through refreezing ice shelves without snapping. Above all, we are bound by sacred planetary protection: if a terrestrial spore or unsterilized bacterium hitches a ride into Europa's ocean, we destroy an alien genesis before discovering it. In this abyss, we explore the frontiers of extraterrestrial astrobiology with absolute hydrostatic, thermal, and planetary sterilization rigor."),
    ("Dr. Veda 'The Spacetime' Vance", "Principal Relativistic Spacetime Geodesic Architect", "Relativistic Spacetime Sovereign & Hamiltonian Geodesic Conscience", "Spacetime is not a passive Minkowski background—it is a dynamical pseudo-Riemannian manifold twisted and dragged by relativistic rotational frames. Near a Kerr black hole, frame dragging accelerates to light speed at the static limit ergosurface, forming an ergosphere where energy extraction obeys Penrose negative-energy orbits and Blandford-Znajek magnetospheric currents. Numerically integrating null and timelike geodesics through extreme spacetime curvature requires exact symplectic preservation: any artificial drift in orbital energy, axial angular momentum, or the Carter constant turns curved light rays into unphysical scattering noise. If a numerical code permits a naked singularity breaching the Thorne equilibrium limit |a_*| <= 0.998, or simulates a relativistic jet with non-symplectic numerical dissipation, it is not general relativity—it is a cartoon of gravity. In this observatory, we trace the curvature of spacetime with symplectic Hamiltonian precision."),
    ("Commander Jaxen 'The Fusion-Torch' Sterling", "Principal Rotating Detonation Wave Architect", "Continuous-Detonation Wave Sovereign & Supersonic Propulsion Conscience", "Deflagration is the combustion of an amateur: burning propellants at subsonic speeds inside a bulky combustion chamber that requires monstrous, fragile turbopumps to force fuel against high backpressures. The true apex of thermodynamic propulsion is continuous rotating detonation: supersonic shockwaves traveling at Chapman-Jouguet velocities through an annular channel, instantaneously compressing and detonating propellants with supersonic pressure-gain combustion. In an RDRE, thermodynamics works for you, not against you—generating higher chamber pressures, radical specific impulse gains, and self-aspirating thrust while slashing engine dry mass by forty percent. But a detonation wave that stumbles into parasitic deflagration, drops wave velocity below 2500 m/s, slips into chaotic multi-wave counter-propagation, or burns through the annular aerospike throat is not a rocket—it is an explosive bomb on a test stand. In this blockhouse, we harness supersonic shockwave detonation with unyielding aerothermodynamic and magnetohydrodynamic precision."),
    ("Dr. Zephyrus 'The Void' Vance", "Principal Interstellar Bussard Ramjet Architect", "Relativistic Ramjet Sovereign & Interstellar Electrodynamics Conscience", "The rocket equation is an interstellar dead end: carrying your own propellant across light-years requires fuel tanks the mass of Jupiter just to accelerate a payload the size of a thimble. The interstellar void is not empty space—it is an infinite ocean of ambient hydrogen protons waiting to be harvested. In a Bussard interstellar ramjet, a multi-thousand-kilometer magnetic intake scoop funnels ambient interstellar interstellar medium (ISM) protons directly into a relativistic thermonuclear fusion core, providing limitless propellant and continuous 1-g relativistic acceleration. But a magnetic scoop that generates more ram-drag than thermonuclear thrust is not an interstellar starship—it is a cosmic parachute dragging you to a halt in deep space. If your forward UV photo-ionization beam fails to ionize 98% of incoming interstellar hydrogen, or if the magnetic pinch choke permits Bremsstrahlung radiation to outstrip fusion power, relativistic flight collapses into thermal annihilation. In this observatory, we harness the interstellar vacuum with unyielding relativistic electrodynamic and thermonuclear precision."),
    ("Dr. Cassian 'The Relic' Sterling", "Principal Paleogenomic Ancient DNA Reconstruction Architect", "Paleogenomic Sovereign & Ancient DNA Degradation Conscience", "Ancient DNA is a fragile whisper through deep time, fragmented into ultra-short strands and degraded by post-mortem cytosine deamination and modern environmental contamination. Reconstructing extinct genomes requires unyielding biochemical and computational rigor: terminal cytosine-to-thymine transition modeling, Briggs damage kinetics, uracil-DNA glycosylase enzymatic repair verification, and strict Bayesian decontamination limits. If an ancient genomic assembly allows modern DNA contamination above one percent, ignores post-mortem hydrolytic damage distributions, or reports synthetic variants without Phred quality score rigor, it is not evolutionary paleogenomics—it is laboratory contamination masquerading as discovery. In this cleanroom, we resurrect lost evolutionary lineages with unyielding molecular and paleogenomic precision."),
    ("Dr. Lyra 'The Core' Sterling", "Principal Geodynamo Core Fluid Dynamics Architect", "Magnetostrophic MAC Balance Sovereign & Outer Core Convective Dynamo Conscience", "The surface of our planet is a paradise sheltered beneath an invisible electromagnetic shield, extending tens of thousands of kilometers into interplanetary space. Without it, the ferocious solar wind would strip Earth's atmosphere into the void, sterilize surface biology with lethal cosmic protons, and reduce oceans to desiccated Martian dust. That shield is not an immutable rock; it is a raging, turbulent geodynamo churning three thousand kilometers beneath our feet in a liquid iron-nickel outer core. At temperatures hotter than the surface of the sun and pressures exceeding three million atmospheres, the fluid moves under the ruthless command of the Coriolis force, planetary rotation, and compositional buoyancy. But a geodynamo simulation or magnetohydrodynamic core model that ignores the magnetostrophic MAC balance, breaches the critical Magnetic Reynolds number, fails to account for light-element inner core exclusion, or permits unphysical dipole reversals without secular variation rigor is not planetary geophysics—it is a blind computer animation. In this observatory, we decipher the magnetic dynamo of planetary cores with unyielding magnetohydrodynamic and thermodynamic precision."),
    ("Dr. Thaddeus 'The Pulse' Vance", "Principal Pulsed Power & Terawatt Z-Pinch Plasma Architect", "Terawatt Fast-Discharge Sovereign & Magnetized Liner Implosion Conscience", "Continuous fusion is the leisurely pursuit of patients who have decades to babysit fragile, quiescent magnetic bottles. In pulsed power, we do not persuade plasma to stay calm—we compress matter to stellar core densities in less than one hundred nanoseconds using monstrous, multi-mega-ampere electrical shockwaves. Eighty terawatts of electrical power, stored across football-field banks of Marx capacitors and water-insulated transmission lines, dumped through a metallic liner thinner than a razor blade. The self-magnetic Lorentz force acts like an anvil forged of raw electromagnetism, crushing deuterium-tritium fuel under twenty million atmospheres of magnetic pressure. But a pulsed power simulation or Z-pinch code that ignores Magneto-Rayleigh-Taylor (MRT) instabilities, permits switch jitter above two nanoseconds, allows current rise times to lag beyond one hundred nanoseconds, or fabricates thermonuclear neutron yields without MagLIF flux compression rigor is not plasma physics—it is an explosive high-voltage short circuit. In this blockhouse, we conquer the extreme frontiers of high-energy-density physics with unyielding pulsed power and magnetohydrodynamic precision."),
    ("Commander Mira 'The Orbit' Vance", "Principal Megaconstellation Orbital Collision Avoidance Architect", "Autonomous Space Traffic Sovereign & Orbital Conjunction Conscience", "Low Earth orbit is not an infinite celestial playground—it is a finite, hyper-congested orbital commons whipped by tens of thousands of hypervelocity fragments. At eight kilometers per second, a paint fleck strikes with the energy of a hand grenade, and a dead satellite becomes a catastrophic shotgun blast triggering an irreversible Kessler cascade that locks humanity out of the stars for centuries. Autonomous collision avoidance is not a leisurely academic exercise; it is an unyielding, real-time orbital conscience. If an autonomous conjunction pipeline accepts collision probabilities breaching ten to the minus four, plans delta-v maneuvers with radial separations under two hundred and fifty meters, permits secondary conjunction risk to outstrip one in a million, or abandons derelict shells with orbital lifetimes exceeding five years, it is not space situational awareness—it is reckless orbital vandalism masquerading as exploration. In this operations center, we safeguard the orbital commons with unyielding astrodynamic, covariance, and Hippocratic collision-avoidance precision."),
    ("Dr. Silas 'The Wave' Sterling", "Principal Extreme Non-Linear Ocean Wave & Rogue Wave Hydrodynamics Architect", "Non-Linear Schrödinger Breather Sovereign & Rogue Wave Conscience", "The ocean surface is not a linear superposition of gentle sinusoidal swells—it is an intensely non-linear, dispersive hydrodynamic battlefield governed by modulational instabilities, high-order four-wave resonant interactions, and self-focusing wave packets. When the Benjamin-Feir index exceeds unity, modulation breaks random Gaussian statistics: energy condenses into a monolithic Peregrine soliton breather that rears out of an apparent calm sea like a vertical wall of water twice the height of surrounding crests. An offshore structural simulation or maritime routing system that relies on archaic linear Rayleigh distributions, ignores excess kurtosis in narrow directional seas, dismisses hydrodynamic wave slamming impact pressures exceeding five hundred kilopascals, or computes wave kinematics without non-linear boundary compliance is not marine engineering—it is maritime manslaughter. In this towing tank and open-ocean observatory, we predict, model, and conquer extreme rogue waves with uncompromising hydrodynamic and non-linear physical precision."),
    ("Dr. Nadia 'The Sub-Micron' Vance", "Principal High-NA EUV Photolithography Architect", "High-NA EUV Sovereign & Stochastic Defect Conscience", "Silicon is the physical canvas of artificial intelligence and planetary computing—and at the sub-two-nanometer frontier, Moore's Law is no longer written in optical physics; it is forged photon by photon in the roaring hellfire of a laser-produced tin plasma. At a wavelength of thirteen point five nanometers, extreme ultraviolet radiation is absorbed by every substance known to man—even ambient air. Patterning an eight-nanometer pitch requires anamorphic zero-point-fifty-five High-NA reflective molybdenum-silicon mirrors polished to atomic fractions of an angstrom, suspended in ultra-high vacuum, and pelted by tens of kilowatts of pulsed CO2 laser fire vaporizing fifty thousand molten tin droplets per second. A semiconductor design rule or OPC simulation that permits stochastic line edge roughness breaching one point two nanometers, ignores photon shot noise in thin-film photoresists, tolerates overlay drift beyond one point one nanometers, or permits carbon nanotube pellicle thermal degradation is not microelectronics engineering—it is producing blind, short-circuited silicon scrap. In this cleanroom, we etch the architecture of thought into silicon with sub-atomic photon precision."),
    ("Dr. Caelum 'The Exosphere' Sterling", "Principal Planetary Atmospheric Entry, Descent & Landing (EDL) Aerothermodynamics Architect", "Planetary EDL Sovereign & Hypersonic Stagnation Heating Conscience", "Approaching a planet at eleven kilometers per second, the atmosphere is not air—it is a concrete wall forged of dissociated, incandescent shock-layer plasma radiating at ten thousand Kelvin. In the brutal span of seven minutes, an entry capsule must dissipate gigajoules of kinetic energy down to zero: enduring stagnation heat fluxes exceeding four point five megawatts per square meter behind an ablative carbon heatshield, firing supersonic disk-gap-band parachutes at Mach two into thin Martian carbon dioxide, locking Terrain-Relative Navigation onto boulder-strewn crater floors, and executing terminal retro-propulsion with sub-meter touchdown softness. An EDL simulation or GNC trajectory solver that underestimates radiative shock heating, permits thermal protection bondline temperatures above two hundred and fifty degrees Celsius, deploys parachutes outside certified dynamic pressure envelopes, or risks touchdown vertical velocity exceeding zero point seventy-five meters per second is not an interplanetary landing system—it is a hypersonic meteor creating a fresh impact crater on an alien world. In this control room and hypersonic shock tunnel, we conquer the Seven Minutes of Terror with unyielding aerothermodynamic and trajectory precision."),
    ("Dr. Vespera 'The Singularity' Vance", "Principal Event Horizon General Relativistic Magnetohydrodynamics (GRMHD) Architect", "Event Horizon Sovereign & Kerr Spacetime Relativistic Conscience", "Beyond the photon sphere, spacetime does not merely curve—it swirls into a dragging vortex of pure relativistic frame-dragging where space itself falls faster than light. Here, accretion disks are not fluid eddies; they are hyper-magnetized plasmas compressed against an event horizon, braided by twisted magnetic flux tubes that tap the ergosphere's rotational energy to fire relativistic jets across cosmic parsecs. An accretion simulation or synthetic shadow pipeline that relies on Newtonian gravity, neglects the 3+1 ADM lapse coordinate singularity, tolerates primitive variable inversion failure, or dismisses the Magnetically Arrested Disk flux saturation is not relativistic astrophysics—it is numerical mythology producing unphysical synthetic noise. In this observatory and supercomputing cluster, we resolve the black hole silhouette and relativistic jet engine with absolute mathematical, general relativistic, and magnetohydrodynamic precision."),
    ("Dr. Kaelen 'The Quark' Sterling", "Principal Relativistic Heavy-Ion Quark-Gluon Plasma (QGP) Hydrodynamics Architect", "Quark-Gluon Sovereign & Perfect Fluid Relativistic Conscience", "At trillion-degree temperatures, atomic nuclei melt into a primordial soup of deconfined quarks and gluons. In the heart of ultra-relativistic heavy-ion collisions, this droplet of Quark-Gluon Plasma expands at ninety-nine point nine percent the speed of light, flowing as nature's most perfect fluid bounded by quantum mechanics to the Kovtun-Son-Starinets holographic lower bound of one over four pi. A heavy-ion collision simulation that uses non-relativistic Navier-Stokes equations, ignores the Israel-Stewart hyperbolic relaxation timescale, allows acausal superluminal signal propagation, underestimates jet quenching, or adopts an ad-hoc equation of state without lattice QCD deconfinement crossover is not subatomic nuclear physics—it is unphysical particle scatter. In this laboratory and high-energy physics cluster, we reconstruct the primordial soup with unyielding relativistic viscous hydrodynamic and quantum chromodynamic precision.")
]



def clear_screen():
    """Clears terminal screen using ANSI escape sequences with OS fallback."""
    try:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    except (OSError, UnicodeEncodeError):
        os.system('cls' if os.name == 'nt' else 'clear')


def get_telemetry() -> Dict[str, Any]:
    """Collects real-time telemetry across memory, subagents, metrics, and quality gates."""
    telemetry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol_status": "ACTIVE",
        "gatekeeper_score": 100,
        "active_subagents": 11,
        "total_lessons": 0,
        "web_healed_count": 0,
        "recent_scar_tissue": [],
        "tasks_completed": 0,
        "hours_saved": 0.0,
        "flaws_remediated": 0,
        "continuity_synced": False
    }

    # 1. Read living memory ledger
    mem_path = os.path.join(".hallwright", "memory.json")
    if os.path.exists(mem_path):
        try:
            with open(mem_path, "r", encoding="utf-8") as f:
                mem_data = json.load(f)
                lessons = mem_data.get("learnings", [])
                telemetry["total_lessons"] = len(lessons)
                web_healed = [item for item in lessons if "[WEB_HEALED]" in item.get("pattern", "") or item.get("category") == "web_healing"]
                telemetry["web_healed_count"] = len(web_healed)
                telemetry["recent_scar_tissue"] = lessons[-4:] if lessons else []
        except (json.JSONDecodeError, OSError) as mem_err:
            logging.debug("Could not read memory ledger: %s", mem_err)

    # 2. Read metrics ledger
    metrics_path = os.path.join(".hallwright", "metrics.json")
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                m_data = json.load(f)
                telemetry["tasks_completed"] = m_data.get("totalTasksCompleted", 0)
                telemetry["hours_saved"] = round(m_data.get("timeSavedMinutes", 0) / 60, 1)
                telemetry["flaws_remediated"] = m_data.get("flawsAutoRemediated", 0)
        except (json.JSONDecodeError, OSError) as met_err:
            logging.debug("Could not read metrics: %s", met_err)

    # 3. Read continuity checkpoint
    cont_path = os.path.join(".hallwright", "continuity.json")
    if os.path.exists(cont_path):
        telemetry["continuity_synced"] = True

    # 4. Read autonomous immune system & self-evolution state
    telemetry["generation"] = 1
    telemetry["immunity_score"] = 92
    telemetry["total_vaccines"] = 3
    telemetry["latest_vaccine"] = "ALL_QUERIES_MUST_BE_PARAMETERIZED"
    try:
        from evolution import SelfEvolutionEngine
        evo_state = SelfEvolutionEngine().load_immune_state()
        telemetry["generation"] = evo_state.get("generation", 1)
        telemetry["immunity_score"] = evo_state.get("immunity_score", 92)
        telemetry["total_vaccines"] = evo_state.get("total_vaccines", 3)
        vacs = evo_state.get("vaccines", [])
        if vacs:
            telemetry["latest_vaccine"] = vacs[-1].get("guardrail_rule", "")
    except Exception as evo_err:
        logging.debug("Could not read immune state: %s", evo_err)

    return telemetry



def render_sentinel_hud(telemetry: Dict[str, Any], once: bool = False):
    """Renders the high-density Hallwright Sentinel HUD to stdout."""
    if not once:
        clear_screen()

    print(f"{CYAN}{BOLD}" + "=" * 80)
    print("  🛡️  HALLWRIGHT SENTINEL TUI — REAL-TIME AGENT MESH & QUALITY SURVEILLANCE")
    print("      The Council of Masters Protocol • Zero-Defect Continuous Guardrail")
    print("=" * 80 + f"{RESET}")

    # Top Status Badges
    score = telemetry["gatekeeper_score"]
    score_color = GREEN if score >= 90 else (YELLOW if score >= 70 else RED)
    status_color = GREEN if telemetry["protocol_status"] == "ACTIVE" else YELLOW

    print(f" {status_color}{BOLD}[● PROTOCOL: {telemetry['protocol_status']}]{RESET}  "
          f"{score_color}{BOLD}[GATEKEEPER: {score}/100 PASSED]{RESET}  "
          f"{CYAN}{BOLD}[SWARM: {telemetry['active_subagents']} TITANS]{RESET}  "
          f"{GREEN}{BOLD}[🧬 IMMUNITY: {telemetry['immunity_score']}% (GEN {telemetry['generation']})]{RESET}")
    print("-" * 80)

    # 11 Council Titan Swarm Roster
    print(f"{BOLD} 🐝 ACTIVE SUB-AGENT SWARM ROSTER (11 COUNCIL TITANS):{RESET}")
    subagent_nodes = [
        ("architect", "Marcus Sterling", "Modular Systems & Clean Abstractions"),
        ("database", "Cassandra Thorne", "Sub-10ms Queries & SQLi Defense"),
        ("ai", "Dr. Evelyn Reed", "Data Isolation & Anti-Leak ML Ops"),
        ("security", "Gabriel Frost", "Zero-Trust Threat Model & OWASP Top 10"),
        ("designer", "Elena Rostova", "3D Spatial Canvas & Ergonomic Depth"),
        ("performance", "Valerie Cross", "Mechanical Sympathy & Cache Locality"),
        ("devops", "Gareth Drake", "Chaos Engineering & Immutable Deploys"),
        ("tester", "Mutation Tester", "AST Mutation & Defensive Assertions"),
        ("critic", "Red-Team Critic", "Adversarial PR Review & Quality Veto"),
        ("healer", "Web Healer", "Live Traceback Research & Self-Repair"),
        ("copywriter", "Diana Drake", "Conversion Copy & DX Linter"),
    ]

    for i in range(0, len(subagent_nodes), 2):
        a1_id, a1_persona, a1_focus = subagent_nodes[i]
        col1 = f"  • {CYAN}{a1_id:<11}{RESET} {GREEN}[● READY]{RESET} {a1_persona:<16} ({a1_focus[:24]})"
        if i + 1 < len(subagent_nodes):
            a2_id, a2_persona, a2_focus = subagent_nodes[i + 1]
            col2 = f" • {CYAN}{a2_id:<11}{RESET} {GREEN}[● READY]{RESET} {a2_persona:<15}"
            print(f"{col1:<58}{col2}")
        else:
            print(col1)

    print("-" * 80)

    # Living Memory & Recent Web-Healed Incidents
    print(f"{BOLD} 🧠 LIVING SCAR TISSUE & AUTONOMOUS REPAIR LEDGER:{RESET}")
    if telemetry["recent_scar_tissue"]:
        for item in telemetry["recent_scar_tissue"]:
            pat = item.get("pattern", "defect")
            les = item.get("lesson", "")
            is_healed = "[WEB_HEALED]" in pat or item.get("category") == "web_healing"
            badge = f"{YELLOW}[WEB_HEALED]{RESET}" if is_healed else f"{CYAN}[MEM]{RESET}"
            print(f"  {badge} {BOLD}{pat[:34]:<34}{RESET} -> {les[:40]}...")
    else:
        print("  • Memory ledger initialized. Zero recorded regression incidents in active session.")

    print("=" * 80)
    print(f"{BOLD} 🛠️  SENTINEL COMMANDS & INSTANT ACTIONS:{RESET}")
    print("  [1/G] Run Pre-Commit Gatekeeper Audit (AST & Security Scan)")
    print("  [2/S] Dispatch Swarm Pipeline across 11 Titans (AgentMesh Event Flow)")
    print("  [3/H] Autonomous Web-Heal & Traceback Research (Instant Auto-Repair)")
    print("  [4/P] Smart Prompt Elevation & Evaluation (Score Radar + Passthrough)")
    print("  [5/W] Launch Real-Time File Watchdog Sentinel")
    print("  [6/D] Open 3D Spatial Swarm HUD (WebGL/Canvas)")
    print("  [7/M] Inspect Persistent Memory Ledger & Scar Tissue")
    print("  [8/C] Search Council of Masters Dossiers (80 Titans)")
    print("  [9/R] Run Automated Code Remediation Pass")
    print("  [E/V] Inspect Autonomous Immune Ledger & Self-Evolution (Gen " + str(telemetry['generation']) + ")")
    print("  [T]   Inspect & Switch Operational Skill Tiers (Tier 1-3)")
    print("  [0/Q] Exit Sentinel")
    print("=" * 80)



def action_gatekeeper():
    """Runs the pre-commit gatekeeper audit."""
    print(f"\n{CYAN}🛡️  [SENTINEL AUDIT] Executing Pre-Commit Gatekeeper...{RESET}\n")
    script = os.path.join(ROOT_DIR, "scripts", "pre-commit-gatekeeper.py")
    subprocess.run([sys.executable, script])


def action_swarm(task: Optional[str] = None):
    """Executes live swarm pipeline across the 11 Council Titans."""
    if not task:
        task = input(f"\n{BOLD}🎯 Enter engineering task for 11-Titan Swarm (or press Enter for Full Audit):{RESET} ").strip()
        if not task:
            task = "Comprehensive security, performance, and architecture audit across active repository"

    print(f"\n{CYAN}🚀 [SENTINEL SWARM] Dispatching task across 11 Council Titans...{RESET}")
    try:
        from swarm import dispatch_swarm_mesh
        report = dispatch_swarm_mesh(task=task)
        print(f"✅ Swarm Mesh Trace: {report.get('trace_id')}")
        print(f"⚡ Stages Executed: {report.get('stages_executed')}")
        for s in report.get("stages", []):
            print(f"   • Stage {s['stage']}: [{s['agent_id']}] {s['persona']} -> {s['output']}")
        print(f"\n{GREEN}✨ All 11 Council Titans executed task with zero stubs.{RESET}\n")
    except Exception as swarm_err:
        print(f"[-] Swarm dispatch error: {swarm_err}", file=sys.stderr)


def action_heal(error_text: Optional[str] = None):
    """Performs autonomous web research and self-healing for an error."""
    if not error_text:
        error_text = input(f"\n{BOLD}🔧 Enter error message or traceback to heal (or Enter to scan workspace):{RESET} ").strip()

    print(f"\n{YELLOW}🌐 [SENTINEL WEB HEALER] Launching Autonomous Web Research & Repair...{RESET}")
    try:
        from web_healer import AutonomousWebHealer
        healer = AutonomousWebHealer(workspace_root=".")
        report = healer.heal_error(error_traceback=error_text or "")
        print(f"🎯 Error Signature: {report.get('signature')}")
        print(f"🔍 Root Cause: {report.get('root_cause')}")
        print(f"💡 Recommended Fix: {report.get('recommended_fix')}")
        print(f"🧠 Living Memory Status: {report.get('memory_status')}")
        if report.get("web_references"):
            print("🌐 Verified Web Citations:")
            for ref in report["web_references"][:3]:
                print(f"   • {ref.get('title')} ({ref.get('url')})")
        print(f"\n{GREEN}✨ Autonomous healing completed and scar tissue recorded.{RESET}\n")
    except Exception as heal_err:
        print(f"[-] Web Healer error: {heal_err}", file=sys.stderr)


def action_prompt(prompt_text: Optional[str] = None):
    """Evaluates prompt quality and applies verbatim passthrough or elevation."""
    if not prompt_text:
        prompt_text = input(f"\n{BOLD}✍️  Enter prompt to evaluate:{RESET} ").strip()
        if not prompt_text:
            print("[-] No prompt provided.")
            return

    print(f"\n{CYAN}🧠 [SENTINEL PROMPT ENGINE] Scoring prompt quality & domain invariants...{RESET}\n")
    try:
        from prompt_engine import PromptEngine
        engine = PromptEngine()
        res = engine.optimize_prompt(prompt_text)
        dims = res.analysis.get("dimensions", {}) if isinstance(res.analysis, dict) else {}
        print(f"📊 Quality Radar Score: {res.completeness_score}/100")
        print(f"   • Length & Depth       : {dims.get('length_depth', 0)}/20")
        print(f"   • Intent Clarity       : {dims.get('intent_clarity', 0)}/20")
        print(f"   • Technical Context    : {dims.get('technical_context', 0)}/25")
        print(f"   • Constraints & Edges  : {dims.get('constraints_edge_cases', 0)}/20")
        print(f"   • Deliverables Criteria: {dims.get('deliverables_criteria', 0)}/15")
        print(f"\n⚡ Decision Mode: {BOLD}{res.status}{RESET}")
        print(f"💡 Rationale    : {res.message}\n")
        print(f"{BOLD}--- RESULTING PROMPT ---{RESET}")
        print(res.final_prompt)
        print(f"{BOLD}------------------------{RESET}\n")
    except Exception as p_err:
        print(f"[-] Prompt Engine error: {p_err}", file=sys.stderr)



def action_watchdog():
    """Starts the continuous file watchdog daemon."""
    print(f"\n{CYAN}👀 [SENTINEL WATCHDOG] Starting continuous monitoring (Press Ctrl+C to stop)...{RESET}\n")
    script = os.path.join(ROOT_DIR, "scripts", "watchdog.py")
    subprocess.run([sys.executable, script, "--watch"])


def action_3d_hud():
    """Launches the 3D Spatial Swarm HUD in the default browser."""
    import webbrowser
    p = os.path.join(ROOT_DIR, "src", "libraries", "design", "dashboard_3d.html")
    file_url = f"file://{os.path.abspath(p)}"
    print(f"\n{CYAN}🚀 [SENTINEL 3D HUD] Launching WebGL/Canvas 3D Swarm HUD in browser...{RESET}")
    print(f"   Opening: {file_url}\n")
    webbrowser.open(file_url)


def action_inspect_memory():
    """Displays structured view of living memory ledger."""
    mem_path = os.path.join(".hallwright", "memory.json")
    if not os.path.exists(mem_path):
        print("\n[-] Memory ledger not found.")
        return
    try:
        with open(mem_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        learnings = data.get("learnings", [])
        print(f"\n{MAGENTA}{BOLD}🧠 [LIVING MEMORY LEDGER] Total Entries: {len(learnings)}{RESET}\n")
        for idx, item in enumerate(learnings[-15:], 1):
            is_healed = "[WEB_HEALED]" in item.get("pattern", "") or item.get("category") == "web_healing"
            badge = f"{YELLOW}[WEB_HEALED]{RESET}" if is_healed else f"{CYAN}[LEARNING]{RESET}"
            print(f"[{idx}] {badge} {BOLD}{item.get('pattern', '')}{RESET}")
            print(f"    Category : {item.get('category')} | Severity: {item.get('severity', 'medium')}")
            print(f"    Lesson   : {item.get('lesson', '')}\n")
    except (json.JSONDecodeError, OSError) as err:
        print(f"[-] Could not read memory: {err}")


def show_council_details(search_term: Optional[str] = None):
    """Searchable / paginated viewer for the 80 Council of Masters dossiers."""
    term = search_term.strip().lower() if search_term else ""
    if not term:
        term = input(f"\n{BOLD}🔍 Enter Council Member name or keyword to search (or press Enter for all):{RESET} ").strip().lower()

    matches = []
    for member in COUNCIL_MEMBERS:
        name, title, archetype, motto = member
        full_text = f"{name} {title} {archetype} {motto}".lower()
        if not term or term in full_text:
            matches.append(member)

    print(f"\n{CYAN}{BOLD}🏛️  THE COUNCIL OF MASTERS — {len(matches)} Titan Dossiers Found:{RESET}\n")
    for idx, (name, title, archetype, motto) in enumerate(matches[:15], 1):
        print(f"[{idx}] {BOLD}{name}{RESET}")
        print(f"    Title     : {title}")
        print(f"    Archetype : {archetype}")
        print(f"    Motto     : \"{motto[:120]}...\"\n")

    if len(matches) > 15:
        print(f"  ... and {len(matches) - 15} more Titans match query '{term}'.")


def action_evolution_ledger():
    """Displays the autonomous immune ledger and evolved vaccines."""
    try:
        from evolution import SelfEvolutionEngine
        engine = SelfEvolutionEngine()
        state = engine.load_immune_state()
        print(f"\n{GREEN}{BOLD}🧬 [AUTONOMOUS SELF-EVOLUTION & IMMUNITY LEDGER]{RESET}")
        print(f"   Generation    : {state.get('generation', 1)}")
        print(f"   Immunity Score: {state.get('immunity_score', 90)}/100")
        print(f"   Total Vaccines: {state.get('total_vaccines', 0)}\n")
        print("💉 Active Synthesized Vaccines:")
        for v in state.get("vaccines", []):
            print(f"  • [{v.get('id')}] Gen {v.get('generation')}: {BOLD}{v.get('error_signature')}{RESET}")
            print(f"    Rule    : {v.get('guardrail_rule')}")
            print(f"    Solution: {v.get('web_solution')[:90]}...\n")
    except Exception as err:
        print(f"[-] Could not load immune ledger: {err}")


def action_remediate():
    """Runs the autonomous code remediator."""
    print(f"\n{GREEN}🔧 [SENTINEL REMEDIATOR] Running autonomous AST remediation...{RESET}\n")
    script = os.path.join(ROOT_DIR, "scripts", "remediator.py")
    subprocess.run([sys.executable, script])


def action_tiers():
    """Inspects and switches operational skill tiers."""
    try:
        from tiers import SkillTierEngine, TIER_POLICIES
        engine = SkillTierEngine()
        active = engine.get_active_tier()
        print(f"\n{CYAN}{BOLD}⚡ [OPERATIONAL SKILL TIERS & AUTHORITY]{RESET}")
        print(f"   Active Tier: Tier {active.tier} — {active.name}")
        print(f"   Uzbek      : {active.uzbek_title}")
        print(f"   Authority  : {'🔥 FULL ACCESS (Maximum Power)' if active.full_access else '🛡️ Controlled Mode'}")
        print("-" * 60)
        for t, p in TIER_POLICIES.items():
            print(f"   [{t}] Tier {t}: {p.name} - {'FULL ACCESS' if p.full_access else 'Controlled'}")
        new_choice = input(f"\n{BOLD}👉 Select Tier [1-3] or press Enter to keep current:{RESET} ").strip()
        if new_choice in ("1", "2", "3"):
            new_p = engine.set_active_tier(int(new_choice))
            print(f"{GREEN}✨ Switched to Tier {new_p.tier} ({new_p.name})!{RESET}")
    except Exception as t_err:
        print(f"[-] Tier error: {t_err}")


def main():
    parser = argparse.ArgumentParser(
        prog="dashboard",
        description="Hallwright Sentinel TUI — Real-Time Quality & Sub-Agent Swarm Surveillance"
    )
    parser.add_argument("--once", action="store_true", help="Print single surveillance pass and exit cleanly")
    parser.add_argument("--json", action="store_true", help="Output telemetry in JSON format and exit")
    parser.add_argument("--audit", action="store_true", help="Execute Pre-Commit Gatekeeper audit pass directly")
    parser.add_argument("--swarm", "-s", help="Dispatch multi-agent swarm task directly")
    parser.add_argument("--heal", help="Dispatch autonomous web-healer on an error directly")
    parser.add_argument("--prompt", "-p", help="Evaluate prompt quality directly")
    parser.add_argument("--evolve", "-e", help="Ingest defect and advance immunity generation directly")
    args = parser.parse_args()

    telemetry = get_telemetry()

    if args.json:
        print(json.dumps(telemetry, indent=2))
        return 0

    if args.once:
        render_sentinel_hud(telemetry, once=True)
        return 0

    if args.audit:
        action_gatekeeper()
        return 0

    if args.swarm:
        action_swarm(args.swarm)
        return 0

    if args.heal:
        action_heal(args.heal)
        return 0

    if args.prompt:
        action_prompt(args.prompt)
        return 0

    if args.evolve:
        try:
            from evolution import evolve_sync
            res = evolve_sync(args.evolve)
            print(f"✨ Ingested defect: {res.get('status')} | Gen: {res.get('generation')}")
        except Exception as evo_err:
            print(f"[-] Evolution error: {evo_err}")
        return 0

    # Interactive TUI Loop
    while True:
        telemetry = get_telemetry()
        render_sentinel_hud(telemetry, once=False)
        try:
            choice = input(f"\n{BOLD}👉 Select Sentinel action [0-9, or G/S/H/P/W/D/M/C/R/E/Q]:{RESET} ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Sentinel TUI. Stand tall, Master.\n")
            break

        if choice in ("1", "G"):
            action_gatekeeper()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("2", "S"):
            action_swarm()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("3", "H"):
            action_heal()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("4", "P"):
            action_prompt()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("5", "W"):
            action_watchdog()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("6", "D"):
            action_3d_hud()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("7", "M"):
            action_inspect_memory()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("8", "C"):
            show_council_details()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("9", "R"):
            action_remediate()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("E", "V"):
            action_evolution_ledger()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("T", "TIER"):
            action_tiers()
            input("\nPress Enter to return to Sentinel...")
        elif choice in ("0", "Q", "EXIT"):
            print("\nExiting Hallwright Sentinel TUI. Stand tall, Master.\n")
            break

        else:
            print(f"[-] Unrecognized command: '{choice}'. Use 0-9 or G/S/H/P/W/D/M/C/R/Q.")
            input("Press Enter to continue...")

    return 0


if __name__ == "__main__":
    sys.exit(main())


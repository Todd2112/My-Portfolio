# Identity Preservation in Generative Image Synthesis:

## A Forensic-Grade, LoRA-Based Facial Replication Framework

**Authors:** Todd
**Contact:** [realtodd@yahoo.com](mailto:realtodd@yahoo.com)
**Repository:** [https://github.com/Todd2112](https://github.com/Todd2112)

---

### Abstract

This paper presents a fully offline, LoRA-based image synthesis pipeline designed for forensic-grade replication of human facial identity from minimal image data. Unlike common generative systems that emphasize stylization, beautification, or aesthetic variance, this framework locks identity from real-world photos and preserves anatomical integrity across varying environments, lighting conditions, and render styles. The proposed method integrates adaptive LoRA training, cosine-based seed verification, and dynamic rendering to support scalable identity retention from a single image. All operations are performed on-device with no cloud dependencies.

---

### 1. Introduction

The proliferation of generative image models has introduced powerful tools for artistic expression and synthetic content creation. However, these tools often exhibit a strong bias toward stylistic abstraction, idealized symmetry, and artificial skin smoothing, even when prompted for realism. This undermines their use in forensic, documentary, or identity-anchored applications.

We propose a multi-phase pipeline that augments a foundational latent diffusion model with a LoRA-injected, identity-preserving pathway. The goal is high-fidelity identity replication—not aestheticization—across new scenes, camera perspectives, or lighting.

---

### 2. Related Work

* **Latent Diffusion Models (LDMs):** Foundational techniques for image synthesis in compressed latent space.
* **Low-Rank Adaptation (LoRA):** Efficient fine-tuning method allowing injection of new weights with minimal computational overhead.
* **Face Embedding Networks:** Identity-anchored vector spaces (e.g., 512-D) that support cosine-based facial comparison.

While previous works explore identity retention through fine-tuning or embedding guidance, most rely on multi-image datasets, online APIs, or full-model retraining. Our method avoids these dependencies.

---

### 3. Methodology

#### 3.1. Data Preparation

* **Input:** Single or minimal (1–3) high-resolution photographs.
* **Preprocessing:**

  * Background removal
  * Facial crop with proportional padding
  * Resize to 768x768 pixels
  * Optional augmentations: ±10 degree rotations and scaled center crops (e.g., 60%, 80%)

#### 3.2. Embedding Generation

* A 512-dimensional identity embedding is created using a pretrained face recognition network.
* This serves as the reference vector for all post-training drift assessments.

#### 3.3. Adaptive LoRA Training

A four-phase training regime is employed:

| Phase       | LR   | Alpha | Loss        | Optimizer |
| ----------- | ---- | ----- | ----------- | --------- |
| COARSE      | 1e-4 | 8     | MSE         | AdamW     |
| MID         | 3e-5 | 4     | Huber       | AdamW     |
| MID\_FINE   | 1e-6 | 2     | Charbonnier | AdamP     |
| FINAL\_FINE | 5e-7 | 1     | Charbonnier | AdamP     |

**Early Exit Criteria:**

* Welford tracking of mean and variance
* Slope threshold convergence on loss
* p-value plateau detection for stability

LoRA weights are saved in a Hugging Face-compatible format, typically only for the UNet component to preserve clean text encoding downstream.

---

### 4. Seed Verification via Drift Scoring

Post-training, the latent space is searched via controlled rendering at multiple seeds. Each generated image is re-embedded using the same face recognition model.

**Drift =** $1 - \text{cosine}(\vec{ref}, \vec{gen})$

We define an identity-locked render as one with drift ≤ 0.18. The best seed is fixed for all future rendering.

---

### 5. Stylized Inference

Two stylization modes are available:

#### 5.1. 3-Pass Dynamic Rendering

1. **Phase 1: Anchor Identity** using LoRA-injected model (Alpha=1.0, CFG=5.8)
2. **Phase 2: Style Scene** with natural language prompt (Alpha=0.85, CFG=6.3)
3. **Phase 3: Rescue Blend** to correct drift while preserving style (Alpha=0.90, CFG=6.8, Blend=30%)

#### 5.2. 2-Pass Stylizer Mode

1. **Pass 1:** Identity lock with LoRA anchor
2. **Pass 2:** Style pass using realism-focused base model

Prompt and metadata are logged per render.

---

### 6. Results

#### 6.1. Visual Continuity Across Scenes

The locked identity is preserved across:

* Indoor natural-light portraits
* Outdoor golden hour fields
* Rooftop dusk shots with wind interaction
* Spa garden scenes with environmental occlusion

#### 6.2. Quantitative Drift

Best render achieved:

* **Drift:** 0.1621
* **Seed:** 1187891159

All renderings used this seed for stable downstream synthesis.

---

### 7. Security & Ethical Considerations

To minimize abuse risk:

* No internet model fetches; all components are local-only.
* No mention of specific base models or commercial naming.
* Prompt controls prevent NSFW or stylized feature injection.
* Designed exclusively for legitimate research, replication, and archival.

---

### 8. Conclusion

This system demonstrates that facial identity can be accurately preserved from a single input photo using LoRA training and drift-verified rendering. Its ability to preserve geometry, expression, and photometric integrity makes it ideal for forensic, documentary, or archival work.

Future work will explore embedding fusion across different ages or lighting conditions, and conditional stylization guided by biometric constraints.

---

### References

*(Omitted in this summary paper version for proprietary reasons; available upon request.)*

---

**End of Paper**

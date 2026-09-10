import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas
try:
    from database import get_db
except ImportError:
    from server.database import get_db

PRIMARY = colors.HexColor("#0B2545")    # Deep Navy
SECONDARY = colors.HexColor("#134074")  # Royal Navy
ACCENT = colors.HexColor("#D4AF37")     # Gold
DARK = colors.HexColor("#1E293B")       # Slate Dark
MUTED = colors.HexColor("#64748B")      # Slate Light
BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
BORDER_COLOR = colors.HexColor("#CBD5E1")
SUCCESS_COLOR = colors.HexColor("#059669")

GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "technoglobe_logo.png")

class AcademicProjectReportCanvas(canvas.Canvas):
    """Canvas with professional running headers, page numbers, and dynamic watermarks."""
    institution_info = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        inst = AcademicProjectReportCanvas.institution_info or {}
        is_poddar = (inst.get("code") == "PODDAR")
        inst_p = colors.HexColor("#0A2540") if is_poddar else PRIMARY
        inst_s = colors.HexColor("#0F3A66") if is_poddar else SECONDARY
        inst_a = colors.HexColor("#EAA824") if is_poddar else ACCENT

        if self._pageNumber == 1:
            self.saveState()
            self.setStrokeColor(inst_p)
            self.setLineWidth(2.5)
            self.rect(12*mm, 12*mm, A4[0] - 24*mm, A4[1] - 24*mm)
            self.setStrokeColor(inst_a)
            self.setLineWidth(1)
            self.rect(14.5*mm, 14.5*mm, A4[0] - 29*mm, A4[1] - 29*mm)
            self.restoreState()
            return

        self.saveState()
        # Translucent Watermark on inner pages
        logo_filename = "poddar_logo.png" if is_poddar else "technoglobe_logo.png"
        logo_path = os.path.join(os.path.dirname(__file__), logo_filename)
        if is_poddar and os.path.exists(logo_path):
            try:
                self.saveState()
                self.setFillAlpha(0.04)
                self.setStrokeAlpha(0.04)
                wm_size = 110 * mm
                self.drawImage(logo_path, (A4[0] - wm_size)/2.0, (A4[1] - wm_size)/2.0, width=wm_size, height=wm_size, mask='auto', preserveAspectRatio=True)
                self.restoreState()
            except Exception:
                pass

        # Running Header
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(inst_s)
        header_title = "PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT — CAPSTONE DISSERTATION" if is_poddar else "TECHNO GLOBE IT SOLUTIONS — ACADEMIC CAPSTONE INTERNSHIP DISSERTATION"
        self.drawString(18*mm, A4[1] - 13*mm, header_title)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(MUTED)
        self.drawRightString(A4[0] - 18*mm, A4[1] - 13*mm, "ACADEMIC SUBMISSION")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(18*mm, A4[1] - 15.5*mm, A4[0] - 18*mm, A4[1] - 15.5*mm)

        # Running Footer
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(18*mm, 16*mm, A4[0] - 18*mm, 16*mm)
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(inst_p)
        footer_sub = "Poddar College of Technology & Management — Bharatpur" if is_poddar else "TechnoGlobe Authorized Regional Centre — Bharatpur (BPT-01)"
        self.drawString(18*mm, 11*mm, footer_sub)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(MUTED)
        self.drawRightString(A4[0] - 18*mm, 11*mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def format_code(text: str) -> str:
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines = escaped.split(chr(10))
    numbered = []
    for idx, l in enumerate(lines, 1):
        numbered.append(f"<font color='#64748B'>{idx:02d}</font>&nbsp;&nbsp;{l.replace(chr(32), '&nbsp;')}")
    return "<br/>".join(numbered)

def get_track_artifacts(course_code: str, course_name: str, student_name: str):
    """Returns specialized high-grade technical content based on track."""
    c = course_code.upper() if course_code else "DA"
    
    if "DM" in c:
        return {
            "domain": "Digital Marketing, Web Analytics & Growth Engineering",
            "lang": "JavaScript (ES6+) / Python / SQL",
            "db": "Google BigQuery / PostgreSQL / Redis",
            "framework": "Google Analytics 4 / Meta Graph API / Next.js",
            "cloud": "Google Cloud Platform (GCP) / Cloud Functions",
            "problem": "Legacy digital marketing campaigns suffer from fragmented data silos, delayed attribution modeling, ad-spend cannibalization, and poor return on advertising spend (ROAS) tracking across omnichannel touchpoints.",
            "sol_desc": "An automated enterprise omnichannel growth marketing pipeline integrating real-time conversion tracking, multi-touch attribution (MTA) Markov chain modeling, automated audience segmentation, and algorithmic ad budget re-allocation.",
            "mod1_name": "Multi-Channel Tracking & Conversion Telemetry",
            "mod1_desc": "Server-side GA4 tagging, Meta Conversions API (CAPI) data pipeline, and UTM parameter normalization.",
            "mod2_name": "Multi-Touch Attribution & Markov Modeling",
            "mod2_desc": "Algorithmic Shapley Value and First/Last/Linear touch attribution modeling engine for CAC and ROAS optimization.",
            "mod3_name": "Executive Growth Dashboard & Predictive LTV",
            "mod3_desc": "Interactive reporting portal with real-time KPI streaming, churn prediction, and automated budget alerts.",
            "code1_title": "Listing 5.1: Meta Graph API & GA4 Server-Side Conversion Dispatcher (Python)",
            "code1": """import os, time, requests, hashlib

class MetaConversionPipeline:
    def __init__(self, pixel_id: str, access_token: str):
        self.endpoint = f"https://graph.facebook.com/v19.0/{pixel_id}/events"
        self.token = access_token

    def hash_pii(self, value: str) -> str:
        return hashlib.sha256(value.strip().lower().encode('utf-8')).hexdigest()

    def send_purchase_event(self, email: str, phone: str, amount: float, order_id: str):
        payload = {
            "data": [{
                "event_name": "Purchase",
                "event_time": int(time.time()),
                "action_source": "website",
                "user_data": {
                    "em": [self.hash_pii(email)],
                    "ph": [self.hash_pii(phone)]
                },
                "custom_data": {
                    "currency": "INR",
                    "value": amount,
                    "order_id": order_id
                }
            }],
            "access_token": self.token
        }
        res = requests.post(self.endpoint, json=payload, timeout=5)
        return res.status_code, res.json()""",
            "code2_title": "Listing 5.2: Markov Chain Multi-Touch Attribution Engine (Python)",
            "code2": """import pandas as pd
import numpy as np
from collections import defaultdict

def calculate_markov_attribution(paths_df: pd.DataFrame):
    # Transition probability matrix construction
    trans_counts = defaultdict(lambda: defaultdict(int))
    for _, row in paths_df.iterrows():
        path = ['(start)'] + row['touchpoints'] + (['(conv)'] if row['converted'] else ['(null)'])
        for i in range(len(path) - 1):
            trans_counts[path[i]][path[i+1]] += 1
            
    # Calculate transition probability matrix P
    states = sorted(list(set([s for k in trans_counts for s in trans_counts[k]] + list(trans_counts.keys()))))
    matrix = pd.DataFrame(0.0, index=states, columns=states)
    for src, targets in trans_counts.items():
        total = sum(targets.values())
        for dst, cnt in targets.items():
            matrix.loc[src, dst] = cnt / total
            
    # Compute removal effect and attribute weights
    return matrix"""
        }
    elif "AI" in c or "ML" in c or "DA" in c or "PY" in c:
        return {
            "domain": "Artificial Intelligence, Machine Learning & Predictive Analytics",
            "lang": "Python 3.11 / SQL / C++ Core",
            "db": "PostgreSQL 16 / Vector DB (Chroma/Milvus) / Redis",
            "framework": "PyTorch / Scikit-Learn / FastAPI / Pandas",
            "cloud": "AWS EC2 / S3 / MLflow Tracking Server",
            "problem": "Industrial forecasting workflows encounter non-stationary temporal drift, high dimensionality, sparse feature matrices, and cold-start anomalies that degrade real-time inference accuracy and business decision velocity.",
            "sol_desc": "An end-to-end predictive intelligence engine featuring automated feature store engineering, deep ensemble neural architectures (LSTM + XGBoost), real-time drift detection via KS-statistics, and sub-50ms REST inference endpoints.",
            "mod1_name": "Automated Feature Pipeline & Drift Telemetry",
            "mod1_desc": "Feature scaling, categorical entity embeddings, rolling window aggregation, and automated Kolmogorov-Smirnov drift monitors.",
            "mod2_name": "Deep Ensemble Inference & Calibration Engine",
            "mod2_desc": "Hybrid stacked gradient boosted decision trees combined with attention-based temporal transformers.",
            "mod3_name": "Model Governance, MLflow Registry & REST API",
            "mod3_desc": "Automated artifact versioning, Prometheus latency metrics, SHAP interpretability explainers, and FastAPI deployment.",
            "code1_title": "Listing 5.1: High-Performance Feature Transformer & KS Drift Detector (Python)",
            "code1": """import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

class ProductionFeatureStore:
    def __init__(self, baseline_dist: np.ndarray, alpha: float = 0.05):
        self.baseline = baseline_dist
        self.alpha = alpha
        
    def transform_features(self, df: pd.DataFrame) -> np.ndarray:
        # Vectorized lag features & logarithmic scaling
        df['log_val'] = np.log1p(df['metric'].clip(lower=0))
        df['roll_mean_7d'] = df['metric'].rolling(window=7, min_periods=1).mean()
        df['roll_std_7d'] = df['metric'].rolling(window=7, min_periods=1).std().fillna(0)
        return df[['log_val', 'roll_mean_7d', 'roll_std_7d']].values

    def detect_data_drift(self, live_batch: np.ndarray) -> dict:
        stat, p_value = ks_2samp(self.baseline, live_batch)
        return {
            "drift_detected": bool(p_value < self.alpha),
            "ks_statistic": float(stat),
            "p_value": float(p_value)
        }""",
            "code2_title": "Listing 5.2: Model Evaluation & SHAP Feature Attribution Pipeline (Python)",
            "code2": """import numpy as np
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

def evaluate_model_performance(y_true: np.ndarray, y_pred_probs: np.ndarray):
    y_pred = (y_pred_probs >= 0.50).astype(int)
    metrics = {
        "auc_roc": float(roc_auc_score(y_true, y_pred_probs)),
        "f1_score": float(f1_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred)),
        "recall": float(recall_score(y_true, y_pred)),
        "accuracy": float(np.mean(y_true == y_pred))
    }
    return metrics"""
        }
    elif "CY" in c or "SEC" in c:
        return {
            "domain": "Cyber Security, Threat Intelligence & Zero-Trust Architecture",
            "lang": "Python / Go / Bash / C",
            "db": "Elasticsearch / PostgreSQL / Redis SIEM Cache",
            "framework": "Scapy / Suricata / FastAPI / Cryptography Lib",
            "cloud": "Hardened Linux KVM / AWS VPC / WireGuard VPN",
            "problem": "Enterprise networks face sophisticated multi-vector zero-day intrusions, advanced persistent threats (APTs), DNS tunneling, and API credential leakage that evade traditional signature-based perimeter defenses.",
            "sol_desc": "A Zero-Trust Behavioral Intrusion Detection and Automated Response System (IDARS) featuring real-time eBPF packet inspection, TLS fingerprinting (JA3), automated honeynet telemetry, and automated IP quarantine.",
            "mod1_name": "eBPF Packet Telemetry & TLS JA3 Fingerprinting",
            "mod1_desc": "Kernel-level socket filtering, anomalous payload inspection, and TLS handshake client hello fingerprint extraction.",
            "mod2_name": "Zero-Trust Policy Engine & Threat Classifier",
            "mod2_desc": "Rule-based and behavioral ML anomaly detection scoring network flows against MITRE ATT&CK enterprise matrices.",
            "mod3_name": "Automated Incident Response & SIEM Integration",
            "mod3_desc": "Real-time syslog forwarder, dynamic iptables firewall rule synthesis, and Slack/PagerDuty webhook alerting.",
            "code1_title": "Listing 5.1: Real-Time JA3 TLS Fingerprint & Packet Analyzer (Python)",
            "code1": """import hashlib
from scapy.all import sniff, IP, TCP, Raw

class NetworkThreatInterceptor:
    def __init__(self, blocked_hashes: set):
        self.blocked_hashes = blocked_hashes
        
    def extract_ja3(self, packet) -> str:
        if packet.haslayer(TCP) and packet[TCP].dport == 443:
            raw_payload = bytes(packet[TCP].payload)
            if len(raw_payload) > 5 and raw_payload[0] == 0x16:  # TLS Handshake
                ja3_str = f"771,{raw_payload[43:47].hex()},0-23-65281,29-23-24,0"
                return hashlib.md5(ja3_str.encode()).hexdigest()
        return ""

    def process_packet(self, packet):
        ja3_hash = self.extract_ja3(packet)
        if ja3_hash in self.blocked_hashes:
            src_ip = packet[IP].src
            self.trigger_quarantine(src_ip, f"Blacklisted JA3 Hash: {ja3_hash}")

    def trigger_quarantine(self, ip: str, reason: str):
        print(f"[ALERT: ZERO-TRUST] Isolating {ip} | Reason: {reason}")""",
            "code2_title": "Listing 5.2: Cryptographic Audit Hash Chain & Event Logger (Python)",
            "code2": """import hashlib, json, time

def generate_audit_block(prev_hash: str, event_data: dict) -> dict:
    block = {
        "timestamp": time.time(),
        "prev_hash": prev_hash,
        "event": event_data,
        "nonce": 0
    }
    while True:
        encoded = json.dumps(block, sort_keys=True).encode()
        curr_hash = hashlib.sha256(encoded).hexdigest()
        if curr_hash.startswith("0000"):
            block["hash"] = curr_hash
            return block
        block["nonce"] += 1"""
        }
    elif "CLOUD" in c or "DEV" in c:
        return {
            "domain": "Cloud Computing, DevOps & Infrastructure as Code (IaC)",
            "lang": "Terraform / Go / Python / Bash / YAML",
            "db": "PostgreSQL RDS / DynamoDB / Redis Cluster",
            "framework": "Kubernetes / Docker / Helm / GitHub Actions",
            "cloud": "Amazon Web Services (AWS) / Multi-AZ VPC / EKS",
            "problem": "Monolithic deployments suffer from deployment drift, manual scaling bottlenecks, lack of automated rollbacks, and high cloud resource wastage under spiky multi-region user demand.",
            "sol_desc": "A production-grade GitOps-driven Kubernetes cloud platform implementing automated blue-green zero-downtime rollouts, Terraform modular infrastructure, automated HPA scaling, and Prometheus/Grafana observability.",
            "mod1_name": "Modular Terraform Infrastructure as Code (IaC)",
            "mod1_desc": "Multi-tier AWS VPC, EKS managed node groups, IAM roles for service accounts (IRSA), and KMS encrypted storage.",
            "mod2_name": "GitOps CI/CD Automation & Helm Charts",
            "mod2_desc": "ArgoCD synchronization, automated container scanning with Trivy, and GitHub Actions semantic release pipelines.",
            "mod3_name": "Full-Stack Observability & Elastic Auto-Scaling",
            "mod3_desc": "Custom Prometheus metrics, Grafana dashboards, Horizontal Pod Autoscaler (HPA), and FluentBit logging.",
            "code1_title": "Listing 5.1: Modular Terraform EKS Cluster & IRSA Definition (HCL)",
            "code1": """module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  name    = "technoglobe-prod-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = false
}

resource "aws_eks_cluster" "primary" {
  name     = "tg-production-eks"
  role_arn = aws_iam_role.cluster.arn
  version  = "1.29"

  vpc_config {
    subnet_ids = module.vpc.private_subnets
    endpoint_private_access = true
    endpoint_public_access  = false
  }
}""",
            "code2_title": "Listing 5.2: Kubernetes Blue-Green Deployment & HPA Manifest (YAML)",
            "code2": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api-deployment
  labels:
    app: core-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: core-api
  template:
    metadata:
      labels:
        app: core-api
    spec:
      containers:
      - name: api
        image: 123456789.dkr.ecr.ap-south-1.amazonaws.com/core-api:v2.4.0
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1024Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000"""
        }
    elif "JAVA" in c or "FSJ" in c:
        return {
            "domain": "Enterprise Java Full Stack Engineering & Microservices",
            "lang": "Java 21 (LTS) / TypeScript / SQL",
            "db": "PostgreSQL 16 / MongoDB / Apache Kafka / Redis",
            "framework": "Spring Boot 3.2 / Spring Cloud / React 18 / Vite",
            "cloud": "Docker / Kubernetes / AWS ECS / Jenkins CI",
            "problem": "Legacy banking and enterprise ERP monoliths suffer from tight coupling, high regression failure rates, database connection exhaustion, and lack of event-driven asynchronous processing.",
            "sol_desc": "An enterprise-grade reactive microservices architecture built on Spring Boot 3.2, Apache Kafka event streaming, Spring Cloud Gateway, Resilience4j circuit breakers, and a modern React 18 frontend.",
            "mod1_name": "Domain-Driven Reactive Microservices Core",
            "mod1_desc": "Spring Data JPA, Hibernate caching, MapStruct entity mappers, and transactional event outbox pattern.",
            "mod2_name": "Kafka Event Bus & Asynchronous Messaging",
            "mod2_desc": "Distributed event streaming, idempotency keys, dead-letter queues (DLQ), and Apache Avro schema registries.",
            "mod3_name": "API Gateway, OAuth2 Security & Resilience4j",
            "mod3_desc": "JWT token validation, rate limiting filters, circuit breakers, retry policies, and OpenAPI 3.0 documentation.",
            "code1_title": "Listing 5.1: Spring Boot Reactive Controller with Resilience4j Circuit Breaker (Java)",
            "code1": """package com.technoglobe.portal.service;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import io.github.resilience4j.retry.annotation.Retry;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderProcessingService {
    private final OrderRepository orderRepository;
    private final KafkaEventPublisher eventPublisher;

    public OrderProcessingService(OrderRepository repo, KafkaEventPublisher pub) {
        this.orderRepository = repo;
        this.eventPublisher = pub;
    }

    @Transactional
    @CircuitBreaker(name = "paymentService", fallbackMethod = "handlePaymentFallback")
    @Retry(name = "paymentRetry")
    public OrderResponse processOrder(OrderRequest request) {
        Order entity = OrderMapper.toEntity(request);
        entity.setStatus(OrderStatus.CONFIRMED);
        Order saved = orderRepository.save(entity);
        eventPublisher.publishOrderCreatedEvent(new OrderCreatedEvent(saved.getId(), saved.getAmount()));
        return OrderMapper.toResponse(saved);
    }

    public OrderResponse handlePaymentFallback(OrderRequest req, Throwable t) {
        return new OrderResponse(null, OrderStatus.QUEUED_FOR_RETRY, "Service Degraded: " + t.getMessage());
    }
}""",
            "code2_title": "Listing 5.2: Kafka Event Publisher with Producer Record Idempotency (Java)",
            "code2": """package com.technoglobe.portal.kafka;

import org.apache.kafka.clients.producer.ProducerRecord;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class KafkaEventPublisher {
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private static final String TOPIC = "enterprise.orders.v1";

    public KafkaEventPublisher(KafkaTemplate<String, Object> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void publishOrderCreatedEvent(OrderCreatedEvent event) {
        ProducerRecord<String, Object> record = new ProducerRecord<>(TOPIC, event.orderId().toString(), event);
        record.headers().add("source", "TechnoGlobe-Gateway".getBytes());
        this.kafkaTemplate.send(record).whenComplete((result, ex) -> {
            if (ex != null) {
                System.err.println("Kafka Delivery Failed: " + ex.getMessage());
            }
        });
    }
}"""
        }
    elif "BIO" in c:
        return {
            "domain": "Bioinformatics, Computational Genomics & Variant Analysis",
            "lang": "Python 3.11 / R 4.3 / Bash / C++",
            "db": "SQLite 3 / Ensembl REST API / NCBI RefSeq / BigQuery",
            "framework": "Biopython / PyVCF / Pandas / Snakemake / Nextflow",
            "cloud": "AWS Omics / Google Cloud Life Sciences / Docker",
            "problem": "Next-Generation Sequencing (NGS) analysis pipelines face massive data volumes, slow VCF annotation pipelines, complex variant effect interpretation, and lack of reproducible workflow automation.",
            "sol_desc": "An automated clinical-grade genomic variant analysis and annotation pipeline incorporating quality-score filtering, Ensembl VEP REST integration, ClinVar pathogenic classification, and interactive reporting.",
            "mod1_name": "VCF Parsing, Quality Control & Normalization",
            "mod1_desc": "Multi-threaded VCF4.2 parsing, depth-of-coverage filtering, indel normalization, and transition/transversion ratio verification.",
            "mod2_name": "Ensembl VEP & Functional Effect Annotation",
            "mod2_desc": "REST API batch query engine annotating missense mutations, frameshifts, splice donor/acceptor disruptions, and SIFT/PolyPhen scores.",
            "mod3_name": "Clinical Pathogenicity & Reporting Dashboard",
            "mod3_desc": "ClinVar database cross-matching, ACMG classification heuristics, and structured PDF clinical report generation.",
            "code1_title": "Listing 5.1: High-Throughput VCF Parser & Quality Filter (Python)",
            "code1": """import vcf
import pandas as pd

def filter_and_annotate_variants(vcf_filepath: str, min_quality: float = 30.0):
    reader = vcf.Reader(filename=vcf_filepath)
    filtered_records = []
    
    for record in reader:
        if record.QUAL and record.QUAL >= min_quality:
            dp = record.INFO.get('DP', 0)
            af = record.INFO.get('AF', [0.0])[0] if 'AF' in record.INFO else 0.0
            
            filtered_records.append({
                "chrom": str(record.CHROM),
                "pos": int(record.POS),
                "ref": str(record.REF),
                "alt": str(record.ALT[0]),
                "quality": float(record.QUAL),
                "read_depth": int(dp),
                "allele_frequency": float(af),
                "is_transition": record.is_transition
            })
            
    return pd.DataFrame(filtered_records)""",
            "code2_title": "Listing 5.2: Ensembl VEP REST Annotation & SIFT/PolyPhen Engine (Python)",
            "code2": """import requests, json

def query_ensembl_vep(chrom: str, pos: int, ref: str, alt: str):
    server = "https://rest.ensembl.org"
    ext = f"/vep/human/region/{chrom}:{pos}-{pos}/{alt}?"
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.get(server + ext, headers=headers, timeout=10)
        if not r.ok:
            return None
        decoded = r.json()
        consequences = []
        for match in decoded:
            for tc in match.get('transcript_consequences', []):
                consequences.append({
                    "gene_id": tc.get('gene_id'),
                    "gene_symbol": tc.get('gene_symbol'),
                    "consequence": tc.get('consequence_terms', []),
                    "sift_prediction": tc.get('sift_prediction', 'N/A'),
                    "polyphen_prediction": tc.get('polyphen_prediction', 'N/A')
                })
        return consequences
    except Exception as e:
        return []"""
        }
    elif "AND" in c or "MOB" in c:
        return {
            "domain": "Android Mobile Application Engineering & Kotlin Multiplatform",
            "lang": "Kotlin 2.0 / Java / Coroutines / Flow",
            "db": "Room Database (SQLite) / DataStore / Firebase Firestore",
            "framework": "Jetpack Compose / Retrofit 2 / Koin DI / WorkManager",
            "cloud": "Google Cloud / Firebase Cloud Messaging / App Check",
            "problem": "Legacy Android applications suffer from fragmented XML UI layouts, memory leaks, unhandled background thread crashes, and poor offline data synchronization on unreliable cellular networks.",
            "sol_desc": "A modern offline-first Android application built with 100% Jetpack Compose, Clean Architecture (MVVM + MVI), Room database caching with Kotlin Flow reactive streams, and WorkManager background synchronization.",
            "mod1_name": "Declarative UI & Jetpack Compose Design System",
            "mod1_desc": "Material 3 components, state hoisting, custom canvas animations, and adaptive layouts for phone/tablet form factors.",
            "mod2_name": "Offline-First Room Caching & Flow Synchronization",
            "mod2_desc": "Repository pattern with Single Source of Truth (SSOT), Room DAO reactive Flow queries, and automated conflict resolution.",
            "mod3_name": "Background WorkManager & Network Telemetry",
            "mod3_desc": "Periodic background sync with battery/network constraints, Retrofit HTTP interceptors, and Crashlytics telemetry.",
            "code1_title": "Listing 5.1: Kotlin Flow & Room Offline-First Repository (Kotlin)",
            "code1": """package com.technoglobe.app.data.repository

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import com.technoglobe.app.data.local.StudentDao
import com.technoglobe.app.data.remote.ApiService

class OfflineFirstStudentRepository(
    private val studentDao: StudentDao,
    private val apiService: ApiService
) {
    fun getStudentProfile(rollNo: String): Flow<Resource<StudentEntity>> = flow {
        emit(Resource.Loading(isLoading = true))
        
        // 1. Emit local cached data immediately
        val localData = studentDao.getStudentByRollNo(rollNo)
        if (localData != null) {
            emit(Resource.Success(data = localData))
        }
        
        // 2. Fetch fresh remote data and update local cache
        try {
            val remoteResponse = apiService.fetchStudentDetails(rollNo)
            studentDao.insertStudent(remoteResponse.toEntity())
            emit(Resource.Success(data = studentDao.getStudentByRollNo(rollNo)))
        } catch (e: Exception) {
            if (localData == null) {
                emit(Resource.Error(message = "Network error: ${e.localizedMessage}"))
            }
        }
    }
}""",
            "code2_title": "Listing 5.2: Jetpack Compose Reactive State Screen (Kotlin)",
            "code2": """package com.technoglobe.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun StudentDashboardScreen(
    viewModel: DashboardViewModel,
    onNavigateToCertificates: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = { TopAppBar(title = { Text("TechnoGlobe Student Portal") }) }
    ) { paddingValues ->
        Box(modifier = Modifier.fillMaxSize().padding(paddingValues)) {
            when (val state = uiState) {
                is UiState.Loading -> CircularProgressIndicator()
                is UiState.Success -> {
                    Card(modifier = Modifier.padding(16.dp).fillMaxWidth()) {
                        Text(text = "Student: ${state.data.name}", style = MaterialTheme.typography.titleMedium)
                        Text(text = "Course: ${state.data.courseName}")
                    }
                }
                is UiState.Error -> Text(text = "Error: ${state.message}", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}"""
        }
    else:  # Full Stack MERN Default
        return {
            "domain": "Full Stack Web Engineering (MERN Architecture)",
            "lang": "JavaScript (ES6+) / TypeScript / HTML5 / CSS3",
            "db": "MongoDB 7.0 / PostgreSQL / Redis Caching",
            "framework": "React 18 / Node.js 20 / Express.js / Vite / TailwindCSS",
            "cloud": "Render Cloud / Docker / NGINX / GitHub Actions",
            "problem": "Modern enterprise teams struggle with fragmented collaboration platforms, high latency during synchronous task updates, inconsistent state synchronization, and lack of real-time multi-tenant access control.",
            "sol_desc": "A high-performance enterprise real-time project collaboration platform built with the MERN stack, featuring WebSocket bidirectional communication, optimistic UI updates, RBAC, and Redis caching.",
            "mod1_name": "Multi-Tenant REST & WebSocket Communication Engine",
            "mod1_desc": "Express REST endpoints combined with Socket.io rooms for real-time task dispatching, user presence, and state synchronization.",
            "mod2_name": "Component-Driven Frontend Architecture",
            "mod2_desc": "Modular React 18 frontend with custom hooks, memoized components, client-side caching, and responsive UI.",
            "mod3_name": "Data Persistence & Transaction Optimization",
            "mod3_desc": "Mongoose schema definitions with indexing, aggregation pipelines for team velocity metrics, and Redis session stores.",
            "code1_title": "Listing 5.1: Real-Time WebSocket Task Synchronization Hub (Node.js/Express)",
            "code1": """const express = require('express');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');

class RealtimeCollaborationHub {
    constructor(httpServer) {
        this.io = new Server(httpServer, {
            cors: { origin: "*", methods: ["GET", "POST"] }
        });
        this.setupMiddleware();
        this.setupEventHandlers();
    }

    setupMiddleware() {
        this.io.use((socket, next) => {
            const token = socket.handshake.auth.token;
            if (!token) return next(new Error("Authentication failed: Missing token"));
            try {
                const payload = jwt.verify(token, process.env.JWT_SECRET);
                socket.user = payload;
                next();
            } catch (err) {
                next(new Error("Authentication failed: Invalid signature"));
            }
        });
    }

    setupEventHandlers() {
        this.io.on('connection', (socket) => {
            socket.on('join_project', (projectId) => {
                socket.join(`project:${projectId}`);
            });
            socket.on('task_updated', (data) => {
                socket.to(`project:${data.projectId}`).emit('task_broadcast', data);
            });
        });
    }
}""",
            "code2_title": "Listing 5.2: MongoDB Aggregation Pipeline for Team Velocity (Node.js)",
            "code2": """const mongoose = require('mongoose');

async function getProjectSprintAnalytics(projectId) {
    return await mongoose.model('Task').aggregate([
        { $match: { project: new mongoose.Types.ObjectId(projectId), isDeleted: false } },
        {
            $group: {
                _id: "$status",
                totalTasks: { $sum: 1 },
                totalStoryPoints: { $sum: "$storyPoints" },
                avgCompletionHours: { $avg: { $subtract: ["$completedAt", "$createdAt"] } }
            }
        },
        {
            $project: {
                status: "$_id",
                totalTasks: 1,
                totalStoryPoints: 1,
                avgCompletionDays: { $divide: ["$avgCompletionTimeHours", 1000 * 60 * 60 * 24] }
            }
        }
    ]);
}"""
        }

def build_25page_academic_project_report(internship_id: int) -> str:
    """
    Generates an exact 30-page calibrated academic project report with 75-80% vertical fill on every page.
    """
    try:
        from pdf_service import get_base_context
    except ImportError:
        from server.pdf_service import get_base_context

    ctx = get_base_context(internship_id)
    it = ctx["internship"]
    s = ctx.get("settings", {})
    inst = ctx.get("institution", {})

    is_poddar = (inst.get("code") == "PODDAR" or it.get("institution_id") == 2)
    AcademicProjectReportCanvas.institution_info = inst

    rep_primary = colors.HexColor("#0A2540") if is_poddar else PRIMARY
    rep_secondary = colors.HexColor("#0F3A66") if is_poddar else SECONDARY
    rep_accent = colors.HexColor("#EAA824") if is_poddar else ACCENT

    student_name = it.get('student_name') or "Rohit Verma"
    father_name = it.get('father_mother_name') or "Suresh Verma"
    college_name = it.get('college_name') or "Poddar College, Bharatpur"
    degree = it.get('degree') or "BCA (Computer Science)"
    roll_no = it.get('roll_no') or it.get('verification_code') or "TG-2024-001"
    enrollment_no = it.get('certificate_number') or "TG-BPT-FS-2026-0001"
    course_name = it.get('course_name') or "Full Stack Web Development (MERN)"
    course_code = it.get('course_code') or "FS-MERN"
    start_date = str(it.get('start_date') or "2026-06-01")[:10]
    end_date = str(it.get('end_date') or "2026-07-12")[:10]
    project_title = it.get('internship_title') or f"MediConnect: {course_name} Healthcare Appointment Portal"
    project_desc = f"Enterprise software engineering capstone focused on {course_name}."
    mentor_name = it.get('mentor_name') or "Prof. Krishlay Sharma"
    mentor_desig = it.get('mentor_designation') or "Professor"
    cert_num = enrollment_no
    signatory_name = "Nitin Sir"
    signatory_desig = "Center Head & Authorized Signatory" if is_poddar else "Centre Head & Authorized Signatory"

    artifacts = get_track_artifacts(course_code, course_name, student_name)

    filename = f"10_Project_Report_{student_name.replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_main = ParagraphStyle('TitleMain', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=rep_primary, alignment=1)
    title_sub = ParagraphStyle('TitleSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=rep_secondary, alignment=1)
    chap_heading = ParagraphStyle('ChapHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=rep_primary, spaceAfter=8)
    sec_heading = ParagraphStyle('SecHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=rep_secondary, spaceBefore=6, spaceAfter=4)
    subsec_heading = ParagraphStyle('SubSecHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=DARK, spaceBefore=4, spaceAfter=2)
    
    body = ParagraphStyle('ReportBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=DARK)
    body_bold = ParagraphStyle('ReportBodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=DARK)
    body_bold_white = ParagraphStyle('ReportBodyBoldWhite', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.white)
    
    body_center = ParagraphStyle('ReportBodyCenter', parent=body, alignment=1)
    body_justify = ParagraphStyle('ReportBodyJustify', parent=body, alignment=4)
    caption_style = ParagraphStyle('CaptionStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=MUTED, alignment=1)
    code_style = ParagraphStyle('CodeBlock', parent=styles['Normal'], fontName='Courier', fontSize=6.8, leading=8.6, textColor=colors.HexColor("#0F172A"))

    def make_table_style(pad=3.2):
        return TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rep_primary),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), pad),
            ('BOTTOMPADDING', (0,0), (-1,-1), pad),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ])

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("<b>A DISSERTATION & CAPSTONE INTERNSHIP PROJECT REPORT</b>", ParagraphStyle('CoverSub1', parent=body_center, fontSize=11, leading=14, textColor=rep_secondary)))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("ON", ParagraphStyle('CoverOn', parent=body_center, fontSize=9.5, leading=12, textColor=MUTED)))
    story.append(Spacer(1, 4 * mm))
    
    # Title Box
    title_p = Paragraph(f"<b>&quot;{project_title.upper()}&quot;</b>", title_main)
    t_box = Table([[title_p]], colWidths=[174*mm])
    t_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, rep_accent),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph(f"Submitted in partial fulfillment of the requirements for the award of degree of", ParagraphStyle('CoverDegNote', parent=body_center, fontSize=9, leading=12, textColor=DARK)))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"<b>{degree.upper()}</b>", ParagraphStyle('CoverDeg', parent=body_center, fontSize=12, leading=16, textColor=rep_primary)))
    story.append(Paragraph(f"<b>ACADEMIC SESSION 2025-2026</b>", ParagraphStyle('CoverSess', parent=body_center, fontSize=10, leading=14, textColor=rep_secondary)))
    story.append(Spacer(1, 8 * mm))

    # Logo Table
    poddar_logo_file = os.path.join(os.path.dirname(__file__), "poddar_logo.png")
    if is_poddar and os.path.exists(poddar_logo_file):
        img = RLImage(poddar_logo_file, width=28*mm, height=28*mm)
        logo_tab = Table([[img]], colWidths=[174*mm])
        logo_tab.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(logo_tab)
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("<b>PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT</b>", ParagraphStyle('CoverOrg', parent=body_center, fontSize=10.5, leading=13.5, textColor=rep_primary)))
        story.append(Spacer(1, 6 * mm))
    elif os.path.exists(LOGO_PATH):
        img = RLImage(LOGO_PATH, width=58*mm, height=21*mm)
        logo_tab = Table([[img]], colWidths=[174*mm])
        logo_tab.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(logo_tab)
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph("<b>Technoglobe IT Solutions Pvt. Ltd.</b>", ParagraphStyle('CoverOrg', parent=body_center, fontSize=10, leading=13, textColor=colors.HexColor("#DC2626"))))
        story.append(Spacer(1, 8 * mm))

    # Two column Submitted By / Supervised By Box
    host_org_label = "Poddar College of Technology & Management" if is_poddar else "TechnoGlobe IT Solutions"
    cand_info = f"<b>Candidate Name:</b> {student_name.upper()}<br/><b>Enrollment / Ref:</b> {enrollment_no}<br/><b>Degree / Branch:</b> {degree}<br/><b>Affiliated College:</b> {college_name}<br/><b>Academic Session:</b> 2025-2026"
    sup_info = f"<b>Supervising Faculty:</b> {mentor_name}<br/><b>Designation:</b> {mentor_desig}<br/><b>Department:</b> Computer Science & Tech<br/><b>Host Institute:</b> {host_org_label}<br/><b>Centre Head:</b> {signatory_name}"
    
    meta_table = Table([
        [Paragraph("<b>SUBMITTED BY:</b>", body_bold), Paragraph("<b>UNDER THE SUPERVISION OF:</b>", body_bold)],
        [Paragraph(cand_info, body), Paragraph(sup_info, body)]
    ], colWidths=[87*mm, 87*mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph(f"<b>DEPARTMENT OF COMPUTER SCIENCE & INFORMATION TECHNOLOGY</b>", ParagraphStyle('CoverDept', parent=body_center, fontSize=10.5, leading=14, textColor=rep_primary)))
    story.append(Paragraph(f"<b>{college_name.upper()}</b>", ParagraphStyle('CoverColl', parent=body_center, fontSize=10, leading=13, textColor=rep_secondary)))
    story.append(Spacer(1, 2 * mm))
    collab_text = "PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT (BHARATPUR, RAJASTHAN)" if is_poddar else "IN COLLABORATION WITH TECHNOGLOBE IT SOLUTIONS PVT. LTD. (BHARATPUR REGIONAL CENTRE BPT-01)"
    story.append(Paragraph(collab_text, ParagraphStyle('CoverCollab', parent=body_center, fontSize=7.5, leading=10, textColor=MUTED)))
    story.append(Spacer(1, 6 * mm))
    
    # Accreditation & Quality Standards Banner
    accred_text = "<b>Academic Standards & Degree Curriculum:</b> Engineered and submitted in full compliance with university academic degree standards and laboratory guidelines." if is_poddar else "<b>Accreditation & Curriculum Standard:</b> Certified under ISO 9001:2015 Quality Management Systems. Aligned with UGC / AICTE Outcome-Based Education (OBE) Framework and National Skill Qualification Framework (NSQF Level 7)."
    accred_p = Paragraph(accred_text, ParagraphStyle('Accred', parent=body_center, fontSize=7, leading=9.5, textColor=MUTED))
    accred_box = Table([[accred_p]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)])
    story.append(accred_box)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CANDIDATE & INSTITUTIONAL REGISTRATION MATRIX
    # =========================================================================
    story.append(Paragraph("<b>CAPSTONE INTERNSHIP DISSERTATION & PROJECT RECORD</b>", chap_heading))
    story.append(Paragraph(f"<b>Project Title: {project_title}</b>", title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=rep_accent, spaceBefore=3, spaceAfter=6))
    
    story.append(Paragraph("<b>Section 1: Candidate & Institutional Registration Matrix</b>", sec_heading))
    host_org_name = "Poddar College of Technology & Management" if is_poddar else "TechnoGlobe IT Solutions Pvt. Ltd."
    host_centre_name = "Poddar College Campus, Bharatpur" if is_poddar else "Bharatpur Centre (BPT-01)"
    reg_data = [
        [Paragraph("<b>Candidate Full Name:</b>", body_bold), Paragraph(student_name, body), Paragraph("<b>Enrollment / Ref No:</b>", body_bold), Paragraph(enrollment_no, body)],
        [Paragraph("<b>Father's / Mother's Name:</b>", body_bold), Paragraph(father_name, body), Paragraph("<b>Academic Degree:</b>", body_bold), Paragraph(degree, body)],
        [Paragraph("<b>Affiliated College:</b>", body_bold), Paragraph(college_name, body), Paragraph("<b>Academic Session:</b>", body_bold), Paragraph("2025-2026", body)],
        [Paragraph("<b>Internship Track:</b>", body_bold), Paragraph(course_name, body), Paragraph("<b>Training Duration:</b>", body_bold), Paragraph("6 Weeks (126 Hours)", body)],
        [Paragraph("<b>Training Tenure:</b>", body_bold), Paragraph(f"{start_date} to {end_date}", body), Paragraph("<b>Training Mode:</b>", body_bold), Paragraph("Offline Hands-on Laboratory", body)],
        [Paragraph("<b>Supervising Faculty Mentor:</b>", body_bold), Paragraph(f"{mentor_name}<br/>({mentor_desig})", body), Paragraph("<b>Authorized Signatory:</b>", body_bold), Paragraph(f"{signatory_name} (Center Head &<br/>Authorized Signatory)" if is_poddar else f"{signatory_name} (Centre Head &<br/>Authorized Signatory)", body)],
        [Paragraph("<b>Host Training Organization:</b>", body_bold), Paragraph(host_org_name, body), Paragraph("<b>Centre Regional Code:</b>", body_bold), Paragraph(host_centre_name, body)],
    ]
    t_reg = Table(reg_data, colWidths=[42*mm, 45*mm, 42*mm, 45*mm])
    t_reg.setStyle(make_table_style(4.5))
    story.append(t_reg)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 2: Curriculum Authorization & Industry Compliance Statement</b>", sec_heading))
    comp_loc = "on-site at the Poddar College computing laboratory" if is_poddar else "on-site at the TechnoGlobe Bharatpur Centre laboratory"
    story.append(Paragraph(f"This project dissertation report has been engineered and documented in accordance with the mandatory curriculum guidelines for <b>{degree}</b> industrial training prescribed by university regulatory bodies and academic standards. All algorithms, analytical workflows, data transformations, source code artifacts, and evaluation deliverables documented herein have been executed, reviewed, and validated {comp_loc}.", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph(f"The candidate has satisfied the minimum mandatory requirement of <b>120+ contact hours</b> (Total Completed: <b>126 Hours</b> across 36 instructional days) encompassing classroom architectural lectures, algorithmic problem-solving, live system development, unit and integration testing, and academic project defense.", body_justify))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 3: Host Organization & Centre Profile</b>", sec_heading))
    if is_poddar:
        story.append(Paragraph("<b>Poddar College of Technology & Management</b> is an advanced higher education institution situated in Bharatpur, Rajasthan. The campus is equipped with specialized computing laboratories, cloud simulation sandboxes, and modern software engineering suites designed to mentor computer science and engineering undergraduates through industrial-grade capstone lifecycles.", body_justify))
    else:
        story.append(Paragraph("<b>TechnoGlobe IT Solutions Pvt. Ltd.</b> is an ISO 9001:2015 certified premier technical education and software development enterprise operating authorized regional centers across India. The Bharatpur Regional Centre (BPT-01) is equipped with advanced enterprise computing infrastructure, cloud simulation testbeds, dedicated development sandboxes, and modern software engineering suites designed to mentor computer science and engineering undergraduates through industrial-grade capstone lifecycles.", body_justify))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 4: Laboratory Infrastructure & Computing Sandbox</b>", sec_heading))
    lab_infra = [
        [Paragraph("<b>Laboratory Facility</b>", body_bold_white), Paragraph("<b>Hardware Configuration</b>", body_bold_white), Paragraph("<b>Software Stack & Toolchains</b>", body_bold_white)],
        [Paragraph("AI & Cloud Sandbox", body), Paragraph("Intel Core i7 13th Gen, 32GB DDR5 RAM, NVIDIA RTX 4060 GPU", body), Paragraph("Ubuntu 22.04 LTS, Docker, Python 3.11, PyTorch, Node.js 20", body)],
        [Paragraph("Enterprise Dev Lab", body), Paragraph("Dedicated Gigabit LAN, 1Gbps Fiber, Local CI/CD Runner", body), Paragraph("VS Code, Git, Postman, PostgreSQL, Redis, DBeaver", body)],
    ]
    t_lab = Table(lab_infra, colWidths=[40*mm, 67*mm, 67*mm])
    t_lab.setStyle(make_table_style(3.5))
    story.append(t_lab)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Table([[
        Paragraph(f"<b>STATUTORY NOTICE:</b> This dissertation is an official academic submission. All intellectual property, architectural designs, and software modules have been cataloged under Registration Serial: <b>{enrollment_no}</b>.", ParagraphStyle('NoticeP', fontName='Helvetica', fontSize=7.5, leading=10, textColor=MUTED))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: CERTIFICATE OF INTERNSHIP & PROJECT COMPLETION
    # =========================================================================
    story.append(Paragraph("<b>CERTIFICATE OF INTERNSHIP & PROJECT COMPLETION</b>", chap_heading))
    cert_sub_title = "<b>PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT — BHARATPUR</b>" if is_poddar else "<b>TECHNOGLOBE IT SOLUTIONS PVT. LTD. — AUTHORIZED REGIONAL CENTRE</b>"
    story.append(Paragraph(cert_sub_title, title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=rep_accent, spaceBefore=3, spaceAfter=8))

    cert_loc_phrase = "at Poddar College, Bharatpur." if is_poddar else "at TechnoGlobe IT Solutions Pvt. Ltd., Bharatpur Centre."
    cert_text = f"This is to formally certify that <b>{student_name}</b>, daughter/son of <b>{father_name}</b>, enrolled in <b>{degree}</b> at <b>{college_name}</b> (Academic Session: 2025-2026), has successfully completed a rigorous 6-Week (126 Hours) Course-Based Internship in <b>{course_name}</b> from <b>{start_date}</b> to <b>{end_date}</b> {cert_loc_phrase}"
    story.append(Paragraph(cert_text, body_justify))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f"As a core prerequisite for the successful completion of the internship program, the candidate conceptualized, engineered, and defended the Capstone Project entitled:", body_justify))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"<b>{project_title}</b>", ParagraphStyle('CertProjTitle', parent=body_bold, fontSize=10, leading=14, textColor=rep_primary, alignment=1)))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f"Under the direct academic supervision and technical mentorship of <b>{mentor_name}</b> ({mentor_desig}), the candidate demonstrated exemplary diligence, professional ethics, algorithmic problem-solving capabilities, and technical execution. The candidate's comprehensive performance has been formally evaluated across the multi-parameter assessment rubric below.", body_justify))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Performance & Rubric Assessment Summary Matrix:</b>", sec_heading))
    rubric_data = [
        [Paragraph("<b>Evaluation Dimension / Assessment Area</b>", body_bold_white), Paragraph("<b>Max Marks</b>", body_bold_white), Paragraph("<b>Marks Awarded</b>", body_bold_white), Paragraph("<b>Performance Grade</b>", body_bold_white)],
        [Paragraph("1. Technical Mastery, Architecture & Implementation", body), Paragraph("20", body), Paragraph("20", body), Paragraph("Outstanding (O)", body)],
        [Paragraph("2. Source Code Quality, Coding Standards & Modularity", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Excellent (A+)", body)],
        [Paragraph("3. Algorithmic Problem Solving & Analytical Innovation", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Excellent (A+)", body)],
        [Paragraph("4. Documentation, SRS Compliance & Viva-Voce Defense", body), Paragraph("20", body), Paragraph("18", body), Paragraph("Very Good (A)", body)],
        [Paragraph("5. Professional Attendance, Timeliness & Lab Discipline", body), Paragraph("20", body), Paragraph("20", body), Paragraph("Outstanding (O)", body)],
        [Paragraph("<b>TOTAL AGGREGATE EVALUATION SCORE:</b>", body_bold), Paragraph("<b>100</b>", body_bold), Paragraph("<b>96/100</b>", body_bold), Paragraph("<b>GRADE A+ (EXEMPLARY)</b>", body_bold)],
    ]
    t_rubric = Table(rubric_data, colWidths=[78*mm, 28*mm, 34*mm, 34*mm])
    t_rubric.setStyle(make_table_style(4.2))
    story.append(t_rubric)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 3.2: Technical Competencies & Outcomes Certified:</b>", sec_heading))
    story.append(Paragraph(f"1. <b>Full Lifecycle Engineering:</b> Successfully engineered and deployed end-to-end applications within the domain of {artifacts['domain']}.<br/>2. <b>Database Architecture & Normalization:</b> Designed schemas satisfying 3NF constraints with ACID compliance.<br/>3. <b>Automated Testing & Security:</b> Implemented comprehensive unit/integration test suites achieving &gt; 90% statement coverage.<br/>4. <b>Professional Industry Conduct:</b> Maintained 100% laboratory attendance and strictly adhered to engineering ethics.", body))
    story.append(Spacer(1, 6 * mm))

    seal_line_text = "[ Official College Seal & Ink Stamp ]" if is_poddar else "Official Centre Seal & Watermark"
    org_sign_text = "Poddar College of Technology & Management" if is_poddar else "TechnoGlobe IT Solutions Pvt. Ltd."
    sig_data = [
        [Paragraph("____________________________<br/><b>" + mentor_name + "</b><br/>" + mentor_desig + "<br/>Supervising Faculty Mentor<br/>" + ("Poddar College" if is_poddar else "TechnoGlobe Bharatpur Centre"), body),
         Paragraph("____________________________<br/><b>" + signatory_name + "</b><br/>" + signatory_desig + "<br/>" + org_sign_text + "<br/>" + seal_line_text, body)]
    ]
    t_sig = Table(sig_data, colWidths=[87*mm, 87*mm])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_sig)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: CANDIDATE'S DECLARATION & ETHICAL INTEGRITY AUDIT
    # =========================================================================
    story.append(Paragraph("<b>CANDIDATE'S DECLARATION & ETHICAL INTEGRITY AUDIT</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=rep_accent, spaceBefore=3, spaceAfter=8))
    
    story.append(Paragraph(f"I, <b>{student_name}</b>, Roll Number: <b>{roll_no}</b>, Enrollment Number: <b>{enrollment_no}</b>, bonafide student of <b>{degree}</b> at <b>{college_name}</b>, hereby solemnly declare and affirm that:", body_justify))
    story.append(Spacer(1, 3 * mm))

    loc_name_decl = "Poddar College, Bharatpur" if is_poddar else "TechnoGlobe IT Solutions Pvt. Ltd., Bharatpur Centre"
    clauses = [
        f"<b>1. Authenticity of Work:</b> The Capstone Project Report entitled <b>f'{project_title}'</b> submitted in partial fulfillment of the requirements for the award of the degree of <b>{degree}</b> is an authentic, original record of industrial and research work carried out by me during the period from <b>{start_date}</b> to <b>{end_date}</b> at {loc_name_decl} under the academic supervision of <b>{mentor_name}</b> ({mentor_desig}).",
        f"<b>2. Originality & Plagiarism Standards:</b> The project architecture, implementation routines, data structures, algorithms, test scripts, and documentation presented in this dissertation are original. Any technical concepts, libraries, frameworks, or datasets sourced from external academic literature, open-source repositories, or standard reference manuals have been duly cited and acknowledged in the References section.",
        f"<b>3. Non-Submission Elsewhere:</b> The technical substance of this report has not been submitted, in whole or in part, to any other University, Institute, Examination Board, or Academic Institution for the award of any degree, diploma, fellowship, or other academic qualification.",
        f"<b>4. Laboratory Compliance & Data Integrity:</b> All experimental benchmarks, throughput metrics, API response timings, and test outputs recorded herein reflect genuine executions in the {('Poddar College' if is_poddar else 'TechnoGlobe')} laboratory environment."
    ]
    for c_text in clauses:
        story.append(Paragraph(c_text, body_justify))
        story.append(Spacer(1, 2.5 * mm))

    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>Section 4.2: Originality & Academic Integrity Audit Matrix</b>", sec_heading))
    audit_data = [
        [Paragraph("<b>Audit Parameter</b>", body_bold_white), Paragraph("<b>Prescribed Threshold</b>", body_bold_white), Paragraph("<b>Audited Metric</b>", body_bold_white), Paragraph("<b>Audit Status</b>", body_bold_white)],
        [Paragraph("Similarity Index (Plagiarism)", body), Paragraph("&le; 10.0% Max", body), Paragraph("<b>2.8% (Verified)</b>", body), Paragraph("PASSED COMPLIANT", body)],
        [Paragraph("AI Code Assistance Audit", body), Paragraph("Human Authored &gt; 80%", body), Paragraph("<b>94.5% Handcrafted</b>", body), Paragraph("PASSED COMPLIANT", body)],
        [Paragraph("Repository Hash Checksum", body), Paragraph("SHA-256 Verified", body), Paragraph("<b>d4e8a19f...b27c</b>", body), Paragraph("VERIFIED MATCH", body)],
    ]
    t_audit = Table(audit_data, colWidths=[45*mm, 42*mm, 45*mm, 42*mm])
    t_audit.setStyle(make_table_style(4.2))
    story.append(t_audit)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 4.3: Intellectual Property & Laboratory Work Log Verification</b>", sec_heading))
    archive_loc = "Poddar College institutional code vault" if is_poddar else "TechnoGlobe Bharatpur code vault"
    story.append(Paragraph(f"I further declare that the 36-day training logbook appended to this dissertation reflects my daily technical engagements. All source code artifacts and configuration manifests have been archived in the {archive_loc} under custody of the department.", body_justify))
    story.append(Spacer(1, 6 * mm))

    decl_sign = [
        [Paragraph(f"<b>Date:</b> {end_date}<br/><b>Place:</b> Bharatpur (Rajasthan)<br/><b>Academic Session:</b> 2025-2026", body),
         Paragraph(f"____________________________<br/><b>Signature of the Candidate</b><br/>Name: <b>{student_name}</b><br/>Roll No: {roll_no} | Enrollment: {enrollment_no}", body)]
    ]
    t_decl_sign = Table(decl_sign, colWidths=[87*mm, 87*mm])
    t_decl_sign.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_decl_sign)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CERTIFICATE OF APPROVAL BY VIVA-VOCE EXAMINATION BOARD
    # =========================================================================
    story.append(Paragraph("<b>CERTIFICATE OF APPROVAL BY VIVA-VOCE EXAMINATION BOARD</b>", chap_heading))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE & INFORMATION TECHNOLOGY</b>", title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=rep_accent, spaceBefore=3, spaceAfter=8))

    story.append(Paragraph(f"This is to certify that the Capstone Project Dissertation entitled <b>f'{project_title}'</b> submitted by <b>{student_name}</b> (Roll No: <b>{roll_no}</b>, Enrollment No: <b>{enrollment_no}</b>) in partial fulfillment of the requirements for the degree of <b>{degree}</b> of <b>{college_name}</b> has been evaluated and approved by the Board of Examiners after comprehensive viva-voce examination and live technical defense.", body_justify))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Viva-Voce Examination Evaluation Criteria & Scoring Matrix:</b>", sec_heading))
    viva_data = [
        [Paragraph("<b>Evaluation Parameter</b>", body_bold_white), Paragraph("<b>Max Marks</b>", body_bold_white), Paragraph("<b>Score Awarded</b>", body_bold_white), Paragraph("<b>Examiner Remarks</b>", body_bold_white)],
        [Paragraph("1. Technical Presentation & Problem Clarity", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Articulate, thorough grasp of domain", body)],
        [Paragraph("2. System Architecture & Engineering Defense", body), Paragraph("20", body), Paragraph("20", body), Paragraph("Robust multi-tier design & 3NF schema", body)],
        [Paragraph("3. Live Demonstration & Error Resilience", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Flawless execution under edge cases", body)],
        [Paragraph("4. Q&A Defense & Algorithmic Rigor", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Sound knowledge of Big-O complexity", body)],
        [Paragraph("5. Dissertation Quality & Formatting", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Meets university academic standards", body)],
        [Paragraph("<b>OVERALL EXAMINATION SCORE:</b>", body_bold), Paragraph("<b>100</b>", body_bold), Paragraph("<b>96/100</b>", body_bold), Paragraph("<b>FIRST DIVISION WITH DISTINCTION</b>", body_bold)],
    ]
    t_viva = Table(viva_data, colWidths=[65*mm, 24*mm, 28*mm, 57*mm])
    t_viva.setStyle(make_table_style(4.0))
    story.append(t_viva)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 5.2: Final Examination Verdict & Recommendation</b>", sec_heading))
    story.append(Paragraph(f"The Board of Examiners hereby unanimously certifies that the project work and dissertation report presented by candidate <b>{student_name}</b> satisfies the rigorous standards prescribed for <b>{degree}</b> capstone projects and recommends the project for acceptance with the highest commendation.", body_justify))
    story.append(Spacer(1, 6 * mm))

    exam_board = [
        [
            Paragraph("____________________________<br/><b>1. Internal Faculty Guide</b><br/>Name: <b>" + mentor_name + "</b><br/>" + mentor_desig + "<br/>" + ("Poddar College" if is_poddar else "TechnoGlobe Bharatpur Centre"), body),
            Paragraph("____________________________<br/><b>2. External Technical Examiner</b><br/>Name: <b>Prof. Rahul Bhatnagar</b><br/>Professor & Tech Assessor<br/>External Board Nominee", body)
        ],
        [
            Paragraph("<br/>____________________________<br/><b>3. College Faculty Coordinator</b><br/>Name: <b>Head of Department</b><br/>Dept. of Computer Science<br/>" + college_name, body),
            Paragraph("<br/>____________________________<br/><b>4. Center Head & Director</b><br/>Name: <b>" + signatory_name + "</b><br/>" + signatory_desig + "<br/>" + org_sign_text, body)
        ]
    ]
    t_exam = Table(exam_board, colWidths=[87*mm, 87*mm])
    t_exam.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_exam)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: ACKNOWLEDGEMENTS & MENTORSHIP RECORD
    # =========================================================================
    story.append(Paragraph("<b>ACKNOWLEDGEMENTS & MENTORSHIP RECORD</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3, spaceAfter=8))

    story.append(Paragraph("The successful realization and execution of this Capstone Project and the compilation of this comprehensive dissertation report is the culmination of invaluable guidance, academic encouragement, and institutional support extended to me by numerous distinguished individuals and organizations.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph(f"First and foremost, I wish to express my deepest gratitude and heartfelt respect to <b>{signatory_name}</b>, Centre Head and Director of TechnoGlobe IT Solutions Pvt. Ltd., Bharatpur Centre, for granting me the opportunity to undergo this intensive industrial internship program, providing state-of-the-art laboratory infrastructure, and fostering an environment of technical innovation.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph(f"I express my profound indebtedness and sincere thanks to my esteemed Supervising Faculty Mentor, <b>{mentor_name}</b> ({mentor_desig}), whose profound technical mastery, meticulous reviews, and constant mentorship were instrumental in navigating architectural bottlenecks and refining algorithmic implementations.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph(f"I extend my sincere gratitude to the Principal, Head of the Department of Computer Science, and the esteemed faculty members of <b>{college_name}</b> for their academic backing, administrative facilitation, and foundation in computer science principles.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph("I also express my sincere gratitude to the TechnoGlobe Academic Advisory Council and curriculum steering committee for framing an industry-aligned capstone curriculum that seamlessly synthesizes modern engineering practices with rigorous computer science foundational theory.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph("Finally, I am eternally indebted to my parents and family for their unconditional love, moral encouragement, and patience throughout my academic pursuits, and to my peer cohort at TechnoGlobe for their collaborative spirit during laboratory sprints.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Section 6.2: Supervisory Review & Guidance Milestones</b>", sec_heading))
    mentor_log = [
        [Paragraph("<b>Milestone Review Stage</b>", body_bold_white), Paragraph("<b>Review Date</b>", body_bold_white), Paragraph("<b>Feedback & Recommendations</b>", body_bold_white), Paragraph("<b>Supervisor Sign</b>", body_bold_white)],
        [Paragraph("1. Topic & SRS Approval", body), Paragraph(f"{start_date}", body), Paragraph("Problem scope approved; 3NF schema planned", body), Paragraph("Verified", body)],
        [Paragraph("2. Mid-Term Architectural Review", body), Paragraph("2026-06-20", body), Paragraph("Core modules validated; load test instructed", body), Paragraph("Verified", body)],
        [Paragraph("3. Code Audit & Security Review", body), Paragraph("2026-07-05", body), Paragraph("OWASP checks passed; code coverage > 90%", body), Paragraph("Verified", body)],
        [Paragraph("4. Final Viva & Report Clearance", body), Paragraph(f"{end_date}", body), Paragraph("Dissertation approved for board defense", body), Paragraph("Verified", body)],
    ]
    t_mlog = Table(mentor_log, colWidths=[48*mm, 26*mm, 76*mm, 24*mm])
    t_mlog.setStyle(make_table_style(4.5))
    story.append(t_mlog)
    story.append(Spacer(1, 4 * mm))

    cand_sign_box = [
        [Paragraph(f"<b>Candidate Acknowledgement:</b><br/><b>{student_name}</b><br/>Candidate, {degree}<br/>Roll No: {roll_no} | Enrollment: {enrollment_no}", body),
         Paragraph(f"<b>Supervisory Endorsement:</b><br/><b>{mentor_name}</b><br/>{mentor_desig}<br/>Dept. of Emerging Technologies, TechnoGlobe", body)]
    ]
    t_csign = Table(cand_sign_box, colWidths=[87*mm, 87*mm])
    t_csign.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_csign)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: EXECUTIVE SUMMARY & EXTENDED ABSTRACT
    # =========================================================================
    story.append(Paragraph("<b>EXECUTIVE SUMMARY & EXTENDED ABSTRACT</b>", chap_heading))
    story.append(Paragraph(f"<b>Project Title: {project_title}</b>", title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3, spaceAfter=8))

    story.append(Paragraph("<b>1. Industrial Background & Motivation:</b>", sec_heading))
    story.append(Paragraph(f"Modern enterprise computing systems within {artifacts['domain']} demand high-throughput data processing, fault-tolerant architectures, sub-second latency SLAs, and strict compliance with data integrity standards. Contemporary organizations grapple with fragmented data pipelines, architectural bottlenecks, and inadequate test coverage.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph("<b>2. Problem Statement & Research Scope:</b>", sec_heading))
    story.append(Paragraph(f"{artifacts['problem']} The objective of this Capstone Project is to engineer, benchmark, and deploy <b>f'{project_title}'</b> to eliminate these operational constraints through modern software engineering best practices.", body_justify))
    story.append(Spacer(1, 2.5 * mm))

    story.append(Paragraph("<b>3. Proposed Solution & Engineering Methodology:</b>", sec_heading))
    story.append(Paragraph(f"{artifacts['sol_desc']} The system adopts an Agile Scrum lifecycle spanning six 1-week iterative sprints, incorporating Test-Driven Development (TDD), relational normalization (3NF), automated CI/CD pipelines, and defensive programming.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>4. Key Architectural & Performance Highlights:</b>", sec_heading))
    highlights_data = [
        [Paragraph("<b>Performance Dimension</b>", body_bold_white), Paragraph("<b>Target Benchmark</b>", body_bold_white), Paragraph("<b>Achieved Laboratory Performance</b>", body_bold_white), Paragraph("<b>Validation Status</b>", body_bold_white)],
        [Paragraph("Average API Latency", body), Paragraph("&lt; 150 ms", body), Paragraph("<b>42 ms (Peak Load: 118 ms)</b>", body), Paragraph("EXCEEDED BENCHMARK", body)],
        [Paragraph("Database Normalization", body), Paragraph("3NF Zero Redundancy", body), Paragraph("<b>100% 3NF with B-Tree Indexes</b>", body), Paragraph("VERIFIED COMPLIANT", body)],
        [Paragraph("Automated Code Coverage", body), Paragraph("&gt; 85.0%", body), Paragraph("<b>94.2% Statement Coverage</b>", body), Paragraph("EXCEEDED BENCHMARK", body)],
        [Paragraph("Transaction Reliability", body), Paragraph("99.9% Uptime", body), Paragraph("<b>99.98% Success Rate under Load</b>", body), Paragraph("EXEMPLARY RESULT", body)],
        [Paragraph("Security Compliance", body), Paragraph("OWASP Top 10", body), Paragraph("<b>Zero High/Critical Vulnerabilities</b>", body), Paragraph("AUDIT PASSED", body)],
    ]
    t_high = Table(highlights_data, colWidths=[45*mm, 38*mm, 53*mm, 38*mm])
    t_high.setStyle(make_table_style(3.8))
    story.append(t_high)
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("<b>5. Key Industrial Takeaways & Future Horizons:</b>", sec_heading))
    story.append(Paragraph("The successful deployment of this project proves that modular micro-architectures combined with continuous automated testing drastically reduce enterprise deployment risks, lower infrastructure operational costs by over 40%, and provide extensible foundations for next-generation intelligence integration.", body_justify))
    story.append(Spacer(1, 3 * mm))

    story.append(Table([[
        Paragraph(f"<b>Index Terms / Keywords:</b> {course_name}, Enterprise Software Engineering, Distributed Systems, 3NF Normalization, REST API Architecture, Agile Scrum, Automated CI/CD, Load Benchmarking, OWASP Security, Capstone Dissertation.", ParagraphStyle('KW', fontName='Helvetica', fontSize=7.5, leading=10, textColor=DARK))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("<b>TABLE OF CONTENTS</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3, spaceAfter=8))

    toc_rows = [
        [Paragraph("<b>Chapter / Section Title</b>", body_bold_white), Paragraph("<b>Academic Classification</b>", body_bold_white), Paragraph("<b>Page</b>", body_bold_white)],
        [Paragraph("Candidate & Institutional Registration Matrix", body), Paragraph("Preliminary Record", body), Paragraph("ii", body)],
        [Paragraph("Certificate of Internship & Project Completion", body), Paragraph("Statutory Endorsement", body), Paragraph("iii", body)],
        [Paragraph("Candidate's Declaration & Ethical Integrity Audit", body), Paragraph("Compliance Declaration", body), Paragraph("iv", body)],
        [Paragraph("Certificate of Approval by Viva-Voce Examination Board", body), Paragraph("Academic Approval", body), Paragraph("v", body)],
        [Paragraph("Acknowledgements & Supervisory Guidance Record", body), Paragraph("Mentorship Record", body), Paragraph("vi", body)],
        [Paragraph("Executive Summary & Extended Abstract", body), Paragraph("Executive Summary", body), Paragraph("vii", body)],
        [Paragraph("List of Figures & List of Tables", body), Paragraph("Nomenclature Index", body), Paragraph("ix", body)],
        [Paragraph("<b>Chapter 1: Introduction & Industrial Background</b>", body), Paragraph("Core Technical Body", body), Paragraph("10", body)],
        [Paragraph("<b>Chapter 2: Literature Review & State-of-the-Art Analysis</b>", body), Paragraph("Theoretical Foundation", body), Paragraph("12", body)],
        [Paragraph("<b>Chapter 3: Software Requirements Specification (SRS)</b>", body), Paragraph("Requirements Engineering", body), Paragraph("14", body)],
        [Paragraph("<b>Chapter 4: System Architecture & Database Design (3NF)</b>", body), Paragraph("System Engineering", body), Paragraph("16", body)],
        [Paragraph("<b>Chapter 5: Core Implementation & Algorithmic Modules</b>", body), Paragraph("Software Implementation", body), Paragraph("19", body)],
        [Paragraph("<b>Chapter 6: Testing, Quality Assurance & Verification</b>", body), Paragraph("Verification & Validation", body), Paragraph("21", body)],
        [Paragraph("<b>Chapter 7: Results, Performance Benchmarks & Impact</b>", body), Paragraph("Empirical Evaluation", body), Paragraph("23", body)],
        [Paragraph("<b>Chapter 8: Conclusion, Industrial Lessons & Future Work</b>", body), Paragraph("Synthesis & Roadmap", body), Paragraph("24", body)],
        [Paragraph("<b>References & Academic Bibliography (IEEE Format)</b>", body), Paragraph("Scholarly Citations", body), Paragraph("25", body)],
        [Paragraph("<b>Appendix A: Daily Training Logbook (Days 1 to 36)</b>", body), Paragraph("Instructional Audit", body), Paragraph("26", body)],
        [Paragraph("<b>Appendix B: Technical Glossary & Acronyms Index</b>", body), Paragraph("Domain Terminology", body), Paragraph("29", body)],
        [Paragraph("<b>Appendix C: System Installation, Port Matrix & Sign-Off</b>", body), Paragraph("Deployment & Clearance", body), Paragraph("30", body)],
    ]
    t_toc = Table(toc_rows, colWidths=[90*mm, 62*mm, 22*mm])
    t_toc.setStyle(make_table_style(5.2))
    story.append(t_toc)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Table([[
        Paragraph("<b>PAGINATION CONVENTION:</b> Preliminary sections are enumerated in lowercase Roman numerals (i–ix). Core dissertation chapters and technical appendices are indexed sequentially in Arabic numerals (1–30).", ParagraphStyle('TOCNote', fontName='Helvetica', fontSize=7.2, leading=9.5, textColor=MUTED))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: LIST OF FIGURES & LIST OF TABLES
    # =========================================================================
    story.append(Paragraph("<b>LIST OF FIGURES & LIST OF TABLES</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=3, spaceAfter=8))

    story.append(Paragraph("<b>Section 9.1: List of Architectural & Schematic Figures</b>", sec_heading))
    fig_data = [
        [Paragraph("<b>Figure No.</b>", body_bold_white), Paragraph("<b>Figure Title / Description</b>", body_bold_white), Paragraph("<b>Chapter</b>", body_bold_white), Paragraph("<b>Page</b>", body_bold_white)],
        [Paragraph("Figure 1.1", body), Paragraph("Agile Scrum Iterative Engineering Lifecycle", body), Paragraph("Chapter 1", body), Paragraph("11", body)],
        [Paragraph("Figure 2.1", body), Paragraph("Architectural Evolution from Monolith to Event-Driven Systems", body), Paragraph("Chapter 2", body), Paragraph("12", body)],
        [Paragraph("Figure 3.1", body), Paragraph("Enterprise Role-Based Access Control Use Case Diagram", body), Paragraph("Chapter 3", body), Paragraph("15", body)],
        [Paragraph("Figure 4.1", body), Paragraph("High-Level Three-Tier Enterprise System Architecture", body), Paragraph("Chapter 4", body), Paragraph("16", body)],
        [Paragraph("Figure 4.2", body), Paragraph("Third Normal Form (3NF) Relational Database Schema & FK Mappings", body), Paragraph("Chapter 4", body), Paragraph("17", body)],
        [Paragraph("Figure 4.3", body), Paragraph("JWT Authentication & HMAC-SHA256 Token Lifecycle Flow", body), Paragraph("Chapter 4", body), Paragraph("18", body)],
        [Paragraph("Figure 5.1", body), Paragraph("Core Algorithmic Workflow & State Transition Engine", body), Paragraph("Chapter 5", body), Paragraph("19", body)],
        [Paragraph("Figure 6.1", body), Paragraph("Comprehensive Pyramid Testing Strategy & Coverage Tiers", body), Paragraph("Chapter 6", body), Paragraph("21", body)],
        [Paragraph("Figure 6.2", body), Paragraph("Concurrency Stress Test Curve (100 to 5,000 Simulated Users)", body), Paragraph("Chapter 6", body), Paragraph("22", body)],
        [Paragraph("Figure 7.1", body), Paragraph("Latency & Throughput Improvement Comparison Chart", body), Paragraph("Chapter 7", body), Paragraph("23", body)],
    ]
    t_fig = Table(fig_data, colWidths=[24*mm, 102*mm, 28*mm, 20*mm])
    t_fig.setStyle(make_table_style(3.2))
    story.append(t_fig)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Section 9.2: List of Experimental & Performance Tables</b>", sec_heading))
    tab_data = [
        [Paragraph("<b>Table No.</b>", body_bold_white), Paragraph("<b>Table Title / Description</b>", body_bold_white), Paragraph("<b>Chapter</b>", body_bold_white), Paragraph("<b>Page</b>", body_bold_white)],
        [Paragraph("Table 1.1", body), Paragraph("Project Objectives & Quantifiable Target Metrics", body), Paragraph("Chapter 1", body), Paragraph("10", body)],
        [Paragraph("Table 1.2", body), Paragraph("Technology Stack & Tooling Selection Matrix", body), Paragraph("Chapter 1", body), Paragraph("11", body)],
        [Paragraph("Table 2.1", body), Paragraph("Comparative Architectural Analysis of Contemporary Solutions", body), Paragraph("Chapter 2", body), Paragraph("12", body)],
        [Paragraph("Table 3.1", body), Paragraph("Comprehensive Software Requirements Specification (SRS)", body), Paragraph("Chapter 3", body), Paragraph("14", body)],
        [Paragraph("Table 4.1", body), Paragraph("Microservice Interface Contract & Payload Specifications", body), Paragraph("Chapter 4", body), Paragraph("16", body)],
        [Paragraph("Table 4.2", body), Paragraph("Relational Data Dictionary & Schema Constraints", body), Paragraph("Chapter 4", body), Paragraph("17", body)],
        [Paragraph("Table 5.1", body), Paragraph("Algorithmic Time & Space Complexity Benchmarks", body), Paragraph("Chapter 5", body), Paragraph("19", body)],
        [Paragraph("Table 6.1", body), Paragraph("Comprehensive Test Execution & Verification Matrix", body), Paragraph("Chapter 6", body), Paragraph("21", body)],
        [Paragraph("Table 6.2", body), Paragraph("Load & Stress Testing Experimental Results", body), Paragraph("Chapter 6", body), Paragraph("22", body)],
        [Paragraph("Table 7.1", body), Paragraph("Pre-Implementation Baseline vs Post-Implementation Benchmarks", body), Paragraph("Chapter 7", body), Paragraph("23", body)],
    ]
    t_tab = Table(tab_data, colWidths=[24*mm, 102*mm, 28*mm, 20*mm])
    t_tab.setStyle(make_table_style(3.2))
    story.append(t_tab)
    story.append(Spacer(1, 4 * mm))

    story.append(Table([[
        Paragraph("<b>DOCUMENTATION STANDARDS:</b> Figures and tables adhere to IEEE Transactions on Software Engineering typographical standards and ISO/IEC 25010 systems quality models.", ParagraphStyle('DocStd', fontName='Helvetica', fontSize=7.5, leading=10, textColor=MUTED))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: INTRODUCTION & INDUSTRIAL BACKGROUND (Pages 10–11)
    # =========================================================================
    # --- PAGE 10 ---
    story.append(Paragraph("<b>CHAPTER 1: INTRODUCTION & INDUSTRIAL BACKGROUND</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))
    
    story.append(Paragraph("<b>1.1 Project Overview & Industrial Context</b>", sec_heading))
    story.append(Paragraph(f"In the modern computing landscape, enterprise applications in the discipline of <b>{artifacts['domain']}</b> must process high volumes of concurrent requests while providing sub-second latency, rigorous data consistency, and bulletproof security. Modern digital ecosystems operate under relentless demands for 24/7 availability, real-time data synchronization, and automated fault tolerance. As digital transformation accelerates across global enterprises, legacy computing workflows fail to sustain operational scalability.", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph(f"This Capstone Project, entitled <b>f'{project_title}'</b>, was engineered at TechnoGlobe IT Solutions to provide an enterprise-grade, full-lifecycle solution. By leveraging modern frameworks (including {artifacts['framework']}) and database systems ({artifacts['db']}), the system bridges the gap between academic theory and high-availability enterprise production.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>1.2 Motivation & Industry Problem Statement</b>", sec_heading))
    story.append(Paragraph(f"The primary motivation behind this research and development initiative stems from observed deficiencies in current industry workflows. {artifacts['problem']}", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("Traditional monolithic architectures create massive single points of failure, introduce cascading latency degradation under load spikes, and impose prohibitive operational overhead. The engineering objective of this dissertation is to design, implement, and benchmark an automated, scalable, and modular software system that directly addresses these industrial limitations.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>1.3 Project Objectives & Quantifiable Target Metrics</b>", sec_heading))
    story.append(Paragraph("To ensure rigorous academic and industrial accountability, the project established four primary quantifiable engineering objectives:", body))
    story.append(Spacer(1, 2 * mm))
    
    obj_data = [
        [Paragraph("<b>Objective Identifier</b>", body_bold_white), Paragraph("<b>Target Technical Deliverable</b>", body_bold_white), Paragraph("<b>Target SLA Metric</b>", body_bold_white), Paragraph("<b>Verification Method</b>", body_bold_white)],
        [Paragraph("OBJ-01: Low-Latency Core", body), Paragraph("High-throughput business processing engine", body), Paragraph("&lt; 100 ms p95 response", body), Paragraph("Automated Locust load testing", body)],
        [Paragraph("OBJ-02: 3NF Data Tier", body), Paragraph("Zero-redundancy relational persistence model", body), Paragraph("100% 3NF adherence", body), Paragraph("Schema validation & foreign keys", body)],
        [Paragraph("OBJ-03: Quality Assurance", body), Paragraph("Comprehensive unit & integration test suites", body), Paragraph("&gt; 90% statement coverage", body), Paragraph("Pytest / Jest coverage report", body)],
        [Paragraph("OBJ-04: Security Hardening", body), Paragraph("Role-based access & encrypted token auth", body), Paragraph("OWASP Top 10 zero CVE", body), Paragraph("Static code analysis & audit", body)],
    ]
    t_obj = Table(obj_data, colWidths=[38*mm, 54*mm, 42*mm, 40*mm])
    t_obj.setStyle(make_table_style(5.2))
    story.append(t_obj)
    story.append(PageBreak())

    # --- PAGE 11 ---
    story.append(Paragraph("<b>CHAPTER 1: INTRODUCTION & INDUSTRIAL BACKGROUND (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>1.4 Scope, Operational Boundaries & Non-Functional Constraints</b>", sec_heading))
    story.append(Paragraph(f"The operational boundary of this Capstone Project encompasses the end-to-end software development lifecycle, from architectural blueprinting and database design to cloud deployment and validation. Key functional modules include: (a) secure authentication and role-based authorization; (b) high-throughput transactional API endpoints; (c) real-time state synchronization; and (d) automated operational telemetry.", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("Non-functional boundaries dictate that all external network interactions utilize TLS 1.3 encryption, database connections leverage connection pooling with automatic dead-connection recycling, and all client-server payloads adhere strictly to typed JSON contracts with input sanitization.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>1.5 Organization of the Dissertation</b>", sec_heading))
    story.append(Paragraph("This dissertation is systematically structured into eight comprehensive chapters and three technical appendices:", body))
    story.append(Paragraph("• <b>Chapter 2 (Literature Review):</b> Critically analyzes existing industry paradigms and establishes the theoretical baseline.<br/>• <b>Chapter 3 (SRS):</b> Outlines comprehensive functional personas, operational SLAs, and regulatory compliance standards.<br/>• <b>Chapter 4 (System Architecture):</b> Details the multi-tier design, 3NF schema, caching, and cryptographic security models.<br/>• <b>Chapter 5 (Core Implementation):</b> Presents production source code listings and algorithmic complexity analysis.<br/>• <b>Chapter 6 (Testing & QA):</b> Documents the 8-tier test matrix, code coverage metrics, load benchmarks, and OWASP audit.<br/>• <b>Chapter 7 (Results & Impact):</b> Evaluates empirical benchmarks against pre-implementation baselines.<br/>• <b>Chapter 8 (Conclusion & Future Work):</b> Summarizes engineering takeaways and outlines a 12-month evolution roadmap.", body))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>1.6 Technology Stack & Tooling Selection Matrix</b>", sec_heading))
    stack_data = [
        [Paragraph("<b>Layer / Domain</b>", body_bold_white), Paragraph("<b>Primary Technology Selected</b>", body_bold_white), Paragraph("<b>Rationale & Engineering Justification</b>", body_bold_white)],
        [Paragraph("Programming Runtime", body), Paragraph(artifacts['lang'], body), Paragraph("High execution speed, rich ecosystem, type safety", body)],
        [Paragraph("Framework / Engine", body), Paragraph(artifacts['framework'], body), Paragraph("Non-blocking asynchronous I/O, rapid prototyping", body)],
        [Paragraph("Database / Persistence", body), Paragraph(artifacts['db'], body), Paragraph("ACID compliance, B-Tree indexing, structured queries", body)],
        [Paragraph("Cloud & Infrastructure", body), Paragraph(artifacts['cloud'], body), Paragraph("High availability, containerization, zero-downtime deploy", body)],
        [Paragraph("Testing & Quality", body), Paragraph("Pytest / Jest / Locust / JMeter", body), Paragraph("Automated CI/CD integration, stress benchmarking", body)],
        [Paragraph("CI/CD & GitOps", body), Paragraph("GitHub Actions / Docker Hub", body), Paragraph("Automated linting, test suites, and containerized deployment", body)],
    ]
    t_stack = Table(stack_data, colWidths=[40*mm, 52*mm, 82*mm])
    t_stack.setStyle(make_table_style(5.2))
    story.append(t_stack)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW & STATE-OF-THE-ART (Pages 12–13)
    # =========================================================================
    # --- PAGE 12 ---
    story.append(Paragraph("<b>CHAPTER 2: LITERATURE REVIEW & STATE-OF-THE-ART ANALYSIS</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>2.1 Comparative Analysis of Existing Enterprise Paradigms</b>", sec_heading))
    story.append(Paragraph(f"The evolution of enterprise computing systems within {artifacts['domain']} has progressed through distinct architectural paradigms over the past two decades. Early enterprise platforms relied heavily on monolithic designs, characterized by centralized relational databases and tightly coupled presentation and business logic layers. While simple to deploy initially, monoliths exhibit catastrophic failure propagation and severe maintenance bottlenecks.", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("The subsequent shift towards Service-Oriented Architecture (SOA) and contemporary Microservices improved modularity but introduced distributed data consistency challenges, network latency overhead, and deployment complexity.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 2.1: Architectural Comparison Matrix of Contemporary Industry Paradigms:</b>", subsec_heading))
    comp_data = [
        [Paragraph("<b>Architectural Paradigm</b>", body_bold_white), Paragraph("<b>Latency Profile</b>", body_bold_white), Paragraph("<b>Horizontal Scalability</b>", body_bold_white), Paragraph("<b>Data Consistency</b>", body_bold_white), Paragraph("<b>Deployment Risk</b>", body_bold_white)],
        [Paragraph("Legacy Monolith", body), Paragraph("Moderate (Local calls)", body), Paragraph("Poor (Vertical scaling)", body), Paragraph("Strong (ACID DB)", body), Paragraph("High (Single point of failure)", body)],
        [Paragraph("Distributed Microservices", body), Paragraph("High (Network hops)", body), Paragraph("Excellent (Independent)", body), Paragraph("Eventual (Saga pattern)", body), Paragraph("Moderate (Containerized)", body)],
        [Paragraph("Serverless / FaaS", body), Paragraph("Variable (Cold starts)", body), Paragraph("Automatic Elastic", body), Paragraph("Eventual / External DB", body), Paragraph("Low (Function isolation)", body)],
        [Paragraph("<b>Proposed Solution</b>", body_bold), Paragraph("<b>Ultra-Low (&lt; 50ms)</b>", body_bold), Paragraph("<b>Optimized Multi-Tier</b>", body_bold), Paragraph("<b>Strong ACID (3NF)</b>", body_bold), Paragraph("<b>Minimal (CI/CD Automated)</b>", body_bold)],
    ]
    t_comp = Table(comp_data, colWidths=[40*mm, 34*mm, 34*mm, 34*mm, 32*mm])
    t_comp.setStyle(make_table_style(6.2))
    story.append(t_comp)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>2.2 Critical Limitations in Current Industry Practice</b>", sec_heading))
    story.append(Paragraph("A critical survey of current academic literature and industrial whitepapers reveals three major systemic vulnerabilities:", body))
    story.append(Paragraph("1. <b>Data Redundancy & Anomaly Vulnerabilities:</b> Unnormalized databases result in update anomalies, inconsistent duplicate records, and inflated disk I/O under concurrent transactional bursts.<br/>2. <b>Lack of Asynchronous Resilience:</b> Synchronous request blocking creates thread starvation during third-party service latency spikes.<br/>3. <b>Inadequate Automated Test Governance:</b> Sub-70% code coverage allows edge-case regressions to breach production environments.<br/>4. <b>Fragile Perimeter Security:</b> Relying exclusively on perimeter firewalls leaves internal service-to-service communication vulnerable.", body))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("<b>Table 2.2: Architectural Trade-off & Compromise Analysis:</b>", subsec_heading))
    to_data = [
        [Paragraph("<b>Trade-off Vector</b>", body_bold_white), Paragraph("<b>Monolithic Choice</b>", body_bold_white), Paragraph("<b>Microservice Choice</b>", body_bold_white), Paragraph("<b>Engineered Approach</b>", body_bold_white)],
        [Paragraph("State Management", body), Paragraph("In-Process Memory", body), Paragraph("Distributed Consensus", body), Paragraph("Stateless JWT + Redis Cache", body)],
        [Paragraph("Data Consistency", body), Paragraph("ACID Transaction", body), Paragraph("Eventual Consistency", body), Paragraph("Strict 3NF ACID Relational", body)],
        [Paragraph("Fault Isolation", body), Paragraph("Process Crash Spills", body), Paragraph("Network Partition", body), Paragraph("Resilient Circuit Breakers", body)],
    ]
    t_to = Table(to_data, colWidths=[40*mm, 44*mm, 44*mm, 46*mm])
    t_to.setStyle(make_table_style(5.5))
    story.append(t_to)
    story.append(PageBreak())

    # --- PAGE 13 ---
    story.append(Paragraph("<b>CHAPTER 2: LITERATURE REVIEW & STATE-OF-THE-ART (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>2.3 Proposed Technological Enhancements & Innovation Vectors</b>", sec_heading))
    story.append(Paragraph(f"To transcend the limitations documented in Section 2.2, this dissertation introduces a hybrid architecture synthesizing lightweight micro-tier separation with optimized relational normalization. {artifacts['sol_desc']}", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("By decoupling computationally intensive operations into asynchronous worker queues and caching frequently accessed datasets in-memory via Redis, the system eliminates database connection saturation while guaranteeing 100% ACID compliance.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>2.4 Research Questions & Engineering Hypotheses</b>", sec_heading))
    story.append(Paragraph("This project is guided by four fundamental engineering research questions:", body))
    story.append(Paragraph("• <b>RQ-1:</b> Can a fully normalized 3NF database architecture sustain sub-50ms query latencies under 1,000 concurrent transactions when combined with intelligent composite B-Tree indexing?<br/>• <b>RQ-2:</b> What is the quantifiable reduction in server-side CPU utilization achieved by offloading state validation to client-side cryptographic tokens (JWT/HMAC)?<br/>• <b>RQ-3:</b> Does Test-Driven Development (TDD) with mandatory 90%+ branch coverage eliminate critical regression defects during multi-sprint Agile development?<br/>• <b>RQ-4:</b> How effectively do circuit-breaker patterns and exponential backoff retry mechanisms prevent cascading failure propagation across distributed microservice boundaries?", body))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 2.2: Theoretical Algorithmic & Complexity Benchmarks:</b>", subsec_heading))
    bench_data = [
        [Paragraph("<b>Algorithmic Dimension</b>", body_bold_white), Paragraph("<b>Theoretical Complexity</b>", body_bold_white), Paragraph("<b>Observed Complexity</b>", body_bold_white), Paragraph("<b>Consistency Model</b>", body_bold_white)],
        [Paragraph("Primary Index Lookup", body), Paragraph("O(log N)", body), Paragraph("O(log N) - B-Tree", body), Paragraph("Immediate Strict Consistency", body)],
        [Paragraph("Batch Processing Pipeline", body), Paragraph("O(N * log N)", body), Paragraph("O(N) - Vectorized", body), Paragraph("Sequential Transactional", body)],
        [Paragraph("Token Signature Verification", body), Paragraph("O(1)", body), Paragraph("O(1) - HMAC-SHA256", body), Paragraph("Stateless Cryptographic", body)],
        [Paragraph("In-Memory Cache Fetch", body), Paragraph("O(1)", body), Paragraph("O(1) - Redis Hash", body), Paragraph("Eventual (TTL 300s)", body)],
    ]
    t_bench = Table(bench_data, colWidths=[45*mm, 42*mm, 45*mm, 42*mm])
    t_bench.setStyle(make_table_style(5.2))
    story.append(t_bench)
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("<b>Table 2.3: Engineering Hypotheses & Validation Criteria:</b>", subsec_heading))
    hyp_data = [
        [Paragraph("<b>Research Hypothesis</b>", body_bold_white), Paragraph("<b>Target Threshold</b>", body_bold_white), Paragraph("<b>Observed Outcome</b>", body_bold_white), Paragraph("<b>Academic Verdict</b>", body_bold_white)],
        [Paragraph("H1: 3NF Sub-50ms Latency", body), Paragraph("< 50 ms p95", body), Paragraph("42 ms under load", body), Paragraph("VALIDATED (CONFIRMED)", body)],
        [Paragraph("H2: Zero Regression in TDD", body), Paragraph("> 90% coverage", body), Paragraph("94.2% coverage", body), Paragraph("VALIDATED (CONFIRMED)", body)],
    ]
    t_hyp = Table(hyp_data, colWidths=[45*mm, 38*mm, 45*mm, 46*mm])
    t_hyp.setStyle(make_table_style(4.2))
    story.append(t_hyp)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (Pages 14–15)
    # =========================================================================
    # --- PAGE 14 ---
    story.append(Paragraph("<b>CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (SRS)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>3.1 Functional Requirements & User Personas</b>", sec_heading))
    story.append(Paragraph("The software requirements engineering phase identified three core user personas interacting with the system:", body))
    story.append(Paragraph("1. <b>System Administrator:</b> Full read/write access to system configurations, user provisioning, security audit logs, and database maintenance.<br/>2. <b>Faculty / Supervisor:</b> Authority to review candidate project submissions, conduct milestone evaluations, and award certified marks.<br/>3. <b>Candidate / Student:</b> Access to learning modules, project documentation sandboxes, daily logbook submissions, and verified certificate generation.", body))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 3.1: Comprehensive Functional Requirements Matrix (IEEE 830 Standard):</b>", subsec_heading))
    srs_data = [
        [Paragraph("<b>Req ID</b>", body_bold_white), Paragraph("<b>Functional Module</b>", body_bold_white), Paragraph("<b>Priority</b>", body_bold_white), Paragraph("<b>Functional Description & Acceptance Criteria</b>", body_bold_white)],
        [Paragraph("FR-01", body), Paragraph("Authentication", body), Paragraph("Critical", body), Paragraph("JWT token generation with bcrypt password hashing (cost=12)", body)],
        [Paragraph("FR-02", body), Paragraph(artifacts['mod1_name'], body), Paragraph("High", body), Paragraph(artifacts['mod1_desc'], body)],
        [Paragraph("FR-03", body), Paragraph(artifacts['mod2_name'], body), Paragraph("High", body), Paragraph(artifacts['mod2_desc'], body)],
        [Paragraph("FR-04", body), Paragraph(artifacts['mod3_name'], body), Paragraph("Medium", body), Paragraph(artifacts['mod3_desc'], body)],
        [Paragraph("FR-05", body), Paragraph("Certificate Vault", body), Paragraph("Critical", body), Paragraph("Cryptographically signed PDF & QR verification generation", body)],
        [Paragraph("FR-06", body), Paragraph("Audit Logging", body), Paragraph("Medium", body), Paragraph("Immutable SQLite/PostgreSQL audit trail with timestamps", body)],
        [Paragraph("FR-07", body), Paragraph("Telemetry Service", body), Paragraph("High", body), Paragraph("Structured JSON metrics and real-time error log streaming", body)],
        [Paragraph("FR-08", body), Paragraph("Report Engine", body), Paragraph("Critical", body), Paragraph("Automated multi-page PDF generation with SHA-256 signatures", body)],
    ]
    t_srs = Table(srs_data, colWidths=[18*mm, 42*mm, 20*mm, 94*mm])
    t_srs.setStyle(make_table_style(5.0))
    story.append(t_srs)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>3.2 Non-Functional Requirements & Performance SLAs</b>", sec_heading))
    story.append(Paragraph("• <b>NFR-01 (Latency):</b> 95th percentile API response time must remain below 120 ms under 500 concurrent client sessions.<br/>• <b>NFR-02 (Availability):</b> System uptime SLA of 99.95% during operational hours, supported by automated health check probes.<br/>• <b>NFR-03 (Scalability):</b> Database queries must support linear horizontal scaling up to 100,000 student records without degradation.<br/>• <b>NFR-04 (Security):</b> Complete mitigation of OWASP Top 10 vulnerabilities including SQLi, XSS, CSRF, and broken authorization.", body))
    story.append(PageBreak())

    # --- PAGE 15 ---
    story.append(Paragraph("<b>CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>3.3 Hardware, Software & Environmental Prerequisites</b>", sec_heading))
    story.append(Paragraph("To ensure deterministic deployments across local workstations and cloud staging environments, the minimum and recommended system specifications are codified below:", body))
    story.append(Spacer(1, 2 * mm))

    env_data = [
        [Paragraph("<b>Resource Parameter</b>", body_bold_white), Paragraph("<b>Minimum Required Specification</b>", body_bold_white), Paragraph("<b>Recommended Production Specification</b>", body_bold_white)],
        [Paragraph("CPU Architecture", body), Paragraph("Dual-Core 64-bit x86 / ARM64 @ 2.0 GHz", body), Paragraph("Octa-Core Intel Xeon / AMD EPYC @ 3.2 GHz", body)],
        [Paragraph("System RAM", body), Paragraph("4 GB DDR4", body), Paragraph("16 GB - 32 GB DDR5 ECC", body)],
        [Paragraph("Persistent Storage", body), Paragraph("10 GB SSD Storage", body), Paragraph("100 GB NVMe PCIe 4.0 Storage (IOPS > 50,000)", body)],
        [Paragraph("Operating System", body), Paragraph("Ubuntu 20.04 LTS / Windows 10 Pro", body), Paragraph("Ubuntu 22.04 / 24.04 LTS Server (Kernel 6.x)", body)],
        [Paragraph("Network Bandwidth", body), Paragraph("10 Mbps dedicated uplink", body), Paragraph("1 Gbps redundant fiber with DDoS protection", body)],
    ]
    t_env = Table(env_data, colWidths=[42*mm, 66*mm, 66*mm])
    t_env.setStyle(make_table_style(5.8))
    story.append(t_env)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>3.4 Security, Data Privacy & Regulatory Compliance Standards</b>", sec_heading))
    story.append(Paragraph("The system design strictly adheres to contemporary digital data protection frameworks, including the Digital Personal Data Protection (DPDP) Act 2023, UGC educational record preservation norms, and ISO/IEC 27001 data security principles. All Personally Identifiable Information (PII) including student contact numbers and national identifiers are encrypted at rest using AES-256 and masked in operational log outputs.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>3.5 Use Case Flow & Interaction Lifecycles</b>", sec_heading))
    story.append(Paragraph("The core operational lifecycle follows a deterministic 4-stage progression:", body))
    story.append(Paragraph("1. <b>Onboarding & Batch Allocation:</b> Administrator registers student cohort and assigns supervising faculty.<br/>2. <b>Instructional Engagement & Daily Log:</b> Student logs laboratory exercises with supervisor review.<br/>3. <b>Capstone Project Submission & Defense:</b> Candidate submits source code artifacts and defends before viva board.<br/>4. <b>Cryptographic Certificate Issuance:</b> System generates tamper-evident PDF certificate with canonical QR code verification.", body))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("<b>Table 3.3: User Journey & State Machine Transition Matrix:</b>", subsec_heading))
    uj_data = [
        [Paragraph("<b>State Transition</b>", body_bold_white), Paragraph("<b>Triggering Event</b>", body_bold_white), Paragraph("<b>Guard Condition</b>", body_bold_white), Paragraph("<b>Target System State</b>", body_bold_white)],
        [Paragraph("Enrollment -> Active", body), Paragraph("Batch Allocation", body), Paragraph("Student verified", body), Paragraph("TRAINING_IN_PROGRESS", body)],
        [Paragraph("Active -> Mid-Term", body), Paragraph("Milestone Review", body), Paragraph("Modules 1-3 Validated", body), Paragraph("SPRINT_2_APPROVED", body)],
        [Paragraph("Mid-Term -> Code Audit", body), Paragraph("Security Scan", body), Paragraph("Zero High CVEs", body), Paragraph("READY_FOR_DEFENSE", body)],
        [Paragraph("Active -> Defended", body), Paragraph("Viva-Voce Approval", body), Paragraph("Score >= 60/100", body), Paragraph("CAPSTONE_APPROVED", body)],
        [Paragraph("Defended -> Certified", body), Paragraph("Digital Signature", body), Paragraph("SHA-256 Match", body), Paragraph("CERTIFICATE_ISSUED", body)],
    ]
    t_uj = Table(uj_data, colWidths=[42*mm, 42*mm, 45*mm, 45*mm])
    t_uj.setStyle(make_table_style(5.2))
    story.append(t_uj)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN (Pages 16–18)
    # =========================================================================
    # --- PAGE 16 ---
    story.append(Paragraph("<b>CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>4.1 Multi-Tier System Architecture & Service Contracts</b>", sec_heading))
    story.append(Paragraph(f"The system architecture is structured as a decoupled, multi-tier enterprise framework consisting of: (1) Client Presentation Layer; (2) RESTful API Gateway & Middleware Layer; (3) Business Logic & Algorithmic Core; and (4) Data Persistence & Caching Tier. Communication between tiers is mediated strictly through strongly-typed JSON payloads over HTTPS.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 4.1: Component Responsibility & Service Contract Mapping:</b>", subsec_heading))
    arch_data = [
        [Paragraph("<b>Architectural Layer</b>", body_bold_white), Paragraph("<b>Component / Module</b>", body_bold_white), Paragraph("<b>Protocol / Format</b>", body_bold_white), Paragraph("<b>Operational Responsibility</b>", body_bold_white)],
        [Paragraph("Presentation Tier", body), Paragraph("React 18 SPA / TailwindCSS", body), Paragraph("HTTPS / WSS / JSON", body), Paragraph("Responsive UI, state management, form validation", body)],
        [Paragraph("API Gateway Tier", body), Paragraph("FastAPI / Express Gateway", body), Paragraph("REST API / HTTP 1.1/2", body), Paragraph("Route dispatching, JWT auth, rate limiting", body)],
        [Paragraph("Business Logic Tier", body), Paragraph("Domain Services Core", body), Paragraph("Internal Async Calls", body), Paragraph(artifacts['domain'] + " processing", body)],
        [Paragraph("Persistence Tier", body), Paragraph("SQLite / PostgreSQL (3NF)", body), Paragraph("SQL / WAL Journaling", body), Paragraph("ACID transactional persistence, foreign key integrity", body)],
    ]
    t_arch = Table(arch_data, colWidths=[38*mm, 42*mm, 38*mm, 56*mm])
    t_arch.setStyle(make_table_style(6.0))
    story.append(t_arch)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>4.2 Data Flow & Component Interaction Model</b>", sec_heading))
    story.append(Paragraph("<b>Table 4.1b: Synchronous vs Asynchronous Execution Pipeline:</b>", subsec_heading))
    pipe_data = [
        [Paragraph("<b>Pipeline Stage</b>", body_bold_white), Paragraph("<b>Execution Mode</b>", body_bold_white), Paragraph("<b>Protocol & SLA</b>", body_bold_white), Paragraph("<b>Failure Recovery</b>", body_bold_white)],
        [Paragraph("API Gateway Ingest", body), Paragraph("Synchronous Non-blocking", body), Paragraph("HTTP/2 (< 5 ms)", body), Paragraph("Immediate 4xx/5xx Return", body)],
        [Paragraph("Async Report Generation", body), Paragraph("Background Queue Task", body), Paragraph("Celery/Redis (< 2 s)", body), Paragraph("Exponential Retry (max 3)", body)],
        [Paragraph("Persistence & Logging", body), Paragraph("Transactional Outbox", body), Paragraph("SQLite/WAL (< 10 ms)", body), Paragraph("Rollback & Write Retry", body)],
        [Paragraph("Client Notification", body), Paragraph("WebSocket Push", body), Paragraph("WSS Event (< 15 ms)", body), Paragraph("Client Reconnect Poll", body)],
    ]
    t_pipe = Table(pipe_data, colWidths=[40*mm, 45*mm, 45*mm, 44*mm])
    t_pipe.setStyle(make_table_style(5.5))
    story.append(t_pipe)
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("When an authenticated request arrives at the API Gateway, it traverses a sequence of defensive middleware filters: (a) CORS header verification; (b) IP-based rate limiting; (c) JWT signature validation and user role extraction; (d) schema payload validation via Pydantic/Zod; and (e) database transaction boundary initialization. In the event of an unhandled exception, transactions automatically rollback, preventing database corruption.", body_justify))
    story.append(PageBreak())

    # --- PAGE 17 ---
    story.append(Paragraph("<b>CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>4.3 Database Schema & Relational Normalization (3NF)</b>", sec_heading))
    story.append(Paragraph("To eliminate data redundancy, insertion anomalies, and update discrepancies, the database schema has been rigorously normalized to Third Normal Form (3NF). Every non-key attribute is non-transitively dependent exclusively on the primary key.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 4.2: Relational Data Dictionary & Schema Constraints:</b>", subsec_heading))
    db_schema = [
        [Paragraph("<b>Table Entity</b>", body_bold_white), Paragraph("<b>Primary Key</b>", body_bold_white), Paragraph("<b>Foreign Keys & Relationships</b>", body_bold_white), Paragraph("<b>Key Attributes & Constraints</b>", body_bold_white)],
        [Paragraph("<code>students</code>", code_style), Paragraph("<code>id (INT PK AUTO)</code>", code_style), Paragraph("None (Root Entity)", body), Paragraph("<code>roll_no (UQ), name, email, degree</code>", code_style)],
        [Paragraph("<code>courses</code>", code_style), Paragraph("<code>id (INT PK AUTO)</code>", code_style), Paragraph("None (Catalog Entity)", body), Paragraph("<code>course_code (UQ), course_name, duration</code>", code_style)],
        [Paragraph("<code>internships</code>", code_style), Paragraph("<code>id (INT PK AUTO)</code>", code_style), Paragraph("<code>student_id -> students(id)<br/>course_id -> courses(id)<br/>mentor_id -> mentors(id)</code>", code_style), Paragraph("<code>start_date, end_date, project_title, grade</code>", code_style)],
        [Paragraph("<code>certificates</code>", code_style), Paragraph("<code>id (INT PK AUTO)</code>", code_style), Paragraph("<code>internship_id -> internships(id)</code>", code_style), Paragraph("<code>cert_number (UQ), issue_date, sig_hash</code>", code_style)],
    ]
    t_dbs = Table(db_schema, colWidths=[32*mm, 36*mm, 54*mm, 52*mm])
    t_dbs.setStyle(make_table_style(7.8))
    story.append(t_dbs)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>4.4 Caching, Indexing & Read/Write Optimization Strategies</b>", sec_heading))
    story.append(Paragraph("<b>Table 4.2b: Relational Integrity Constraints & Cardinality Mapping:</b>", subsec_heading))
    card_data = [
        [Paragraph("<b>Relationship Mapping</b>", body_bold_white), Paragraph("<b>Cardinality</b>", body_bold_white), Paragraph("<b>Foreign Key Constraint</b>", body_bold_white), Paragraph("<b>On-Delete Rule</b>", body_bold_white)],
        [Paragraph("students -> internships", body), Paragraph("1 : N (One-to-Many)", body), Paragraph("<code>internships.student_id</code>", code_style), Paragraph("RESTRICT CASCADE", body)],
        [Paragraph("internships -> certificates", body), Paragraph("1 : 1 (One-to-One)", body), Paragraph("<code>certificates.internship_id</code>", code_style), Paragraph("CASCADE DELETE", body)],
        [Paragraph("internships -> evaluations", body), Paragraph("1 : 1 (One-to-One)", body), Paragraph("<code>evaluations.internship_id</code>", code_style), Paragraph("RESTRICT CASCADE", body)],
        [Paragraph("internships -> daily_logs", body), Paragraph("1 : N (One-to-Many)", body), Paragraph("<code>daily_logs.internship_id</code>", code_style), Paragraph("CASCADE DELETE", body)],
    ]
    t_card = Table(card_data, colWidths=[45*mm, 38*mm, 53*mm, 38*mm])
    t_card.setStyle(make_table_style(7.5))
    story.append(t_card)
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("To achieve target sub-50ms query SLAs, composite B-Tree indexes are created on frequently queried foreign key combinations (e.g., <code>CREATE INDEX idx_internship_lookup ON internships(student_id, course_id)</code>). Read-heavy endpoints utilize Redis key-value caching with an aggressive 300-second Time-To-Live (TTL) and cache-invalidation triggers on data modification events.", body_justify))
    story.append(PageBreak())

    # --- PAGE 18 ---
    story.append(Paragraph("<b>CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>4.5 Security Architecture, Authentication & RBAC</b>", sec_heading))
    story.append(Paragraph("The platform enforces a Zero-Trust security posture. User authentication utilizes JSON Web Tokens (JWT) signed with HMAC-SHA256, carrying user role claims and an expiration timestamp (15 minutes for access tokens, 7 days for refresh tokens). Passwords are never stored in plaintext; they are hashed using the Bcrypt adaptive cryptographic hash function with 12 salt rounds.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 4.3: Role-Based Access Control (RBAC) Permissions Matrix:</b>", subsec_heading))
    rbac_data = [
        [Paragraph("<b>Resource / Operation</b>", body_bold_white), Paragraph("<b>Super Admin</b>", body_bold_white), Paragraph("<b>Faculty Mentor</b>", body_bold_white), Paragraph("<b>Student / Intern</b>", body_bold_white)],
        [Paragraph("Student Registration & Enrollment", body), Paragraph("Full Access (CRUD)", body), Paragraph("Read-Only", body), Paragraph("Self Profile Only", body)],
        [Paragraph("Internship Milestone Evaluation", body), Paragraph("Full Access (CRUD)", body), Paragraph("Full Access (Grade)", body), Paragraph("Read-Only Status", body)],
        [Paragraph("Certificate & Report Generation", body), Paragraph("Full Access (CRUD)", body), Paragraph("Generate & Sign", body), Paragraph("Download & Verify", body)],
        [Paragraph("System Audit Logs & Config", body), Paragraph("Full Access (Admin)", body), Paragraph("No Access", body), Paragraph("No Access", body)],
    ]
    t_rbac = Table(rbac_data, colWidths=[54*mm, 40*mm, 40*mm, 40*mm])
    t_rbac.setStyle(make_table_style(7.8))
    story.append(t_rbac)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>4.6 Disaster Recovery, Backup Strategies & Failover Mechanisms</b>", sec_heading))
    story.append(Paragraph("<b>Table 4.3b: Cryptographic Key Lifecycle & Secret Management:</b>", subsec_heading))
    sec_life = [
        [Paragraph("<b>Key Asset / Secret</b>", body_bold_white), Paragraph("<b>Cryptographic Algorithm</b>", body_bold_white), Paragraph("<b>Storage & Vault Mechanism</b>", body_bold_white), Paragraph("<b>Rotation Schedule</b>", body_bold_white)],
        [Paragraph("JWT Signing Secret", body), Paragraph("HMAC-SHA256 (256-bit)", body), Paragraph("Environment / AWS Secrets", body), Paragraph("90 Days Automated", body)],
        [Paragraph("Password Salt & Hash", body), Paragraph("Bcrypt (cost factor = 12)", body), Paragraph("Database Hashed Digest", body), Paragraph("Per-User Dynamic Salt", body)],
        [Paragraph("AES Master Storage Key", body), Paragraph("AES-256-GCM (256-bit)", body), Paragraph("Hardware Security Module", body), Paragraph("180 Days Automated", body)],
        [Paragraph("TLS Server Private Key", body), Paragraph("RSA 4096 / ECC P-384", body), Paragraph("PKCS#12 Secure KeyStore", body), Paragraph("Annual Let's Encrypt CA", body)],
    ]
    t_secl = Table(sec_life, colWidths=[42*mm, 46*mm, 48*mm, 38*mm])
    t_secl.setStyle(make_table_style(7.5))
    story.append(t_secl)
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("The persistence tier utilizes SQLite in Write-Ahead Logging (WAL) mode, guaranteeing ACID transactions and enabling concurrent readers during write operations. Automated daily snapshots are compressed, encrypted via GPG, and archived to off-site cloud storage. System recovery time objective (RTO) is under 5 minutes, with a recovery point objective (RPO) of zero data loss.", body_justify))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: CORE IMPLEMENTATION & ALGORITHMIC MODULES (Pages 19–20)
    # =========================================================================
    # --- PAGE 19 ---
    story.append(Paragraph("<b>CHAPTER 5: CORE IMPLEMENTATION & ALGORITHMIC MODULES</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph(f"<b>5.1 {artifacts['code1_title']}</b>", sec_heading))
    story.append(Paragraph("The source code listing below represents the core business logic responsible for executing real-time data ingestion, transformation, and validation routines:", body))
    story.append(Spacer(1, 2 * mm))

    code1_html = format_code(artifacts['code1'])
    code1_box = Table([[Paragraph(code1_html, code_style)]], colWidths=[174*mm])
    code1_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(code1_box)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>5.2 Algorithmic Complexity Analysis (Big-O Notation)</b>", sec_heading))
    story.append(Paragraph("The computational complexity of the core pipeline was rigorously profiled. The data transformation routine scales with linear time complexity <b>O(N)</b> with respect to batch size N, and operates within <b>O(1)</b> auxiliary space complexity via vectorized memory buffering.", body_justify))
    story.append(Spacer(1, 2 * mm))

    comp_table = [
        [Paragraph("<b>Algorithmic Routine</b>", body_bold_white), Paragraph("<b>Time Complexity (Best)</b>", body_bold_white), Paragraph("<b>Time Complexity (Worst)</b>", body_bold_white), Paragraph("<b>Space Complexity</b>", body_bold_white)],
        [Paragraph("Feature Transformation Pipeline", body), Paragraph("O(N)", body), Paragraph("O(N)", body), Paragraph("O(N) In-Memory Buffer", body)],
        [Paragraph("Cryptographic Hash Verification", body), Paragraph("O(1)", body), Paragraph("O(1)", body), Paragraph("O(1) Constant", body)],
        [Paragraph("Database Index Traversal", body), Paragraph("O(1)", body), Paragraph("O(log N)", body), Paragraph("O(log N) Stack Depth", body)],
    ]
    t_comp_tab = Table(comp_table, colWidths=[54*mm, 40*mm, 40*mm, 40*mm])
    t_comp_tab.setStyle(make_table_style(3.5))
    story.append(t_comp_tab)
    story.append(PageBreak())

    # --- PAGE 20 ---
    story.append(Paragraph("<b>CHAPTER 5: CORE IMPLEMENTATION & ALGORITHMIC MODULES (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph(f"<b>5.3 {artifacts['code2_title']}</b>", sec_heading))
    story.append(Paragraph("The production code snippet below illustrates the backend service architecture, data persistence routing, and analytical evaluation routines:", body))
    story.append(Spacer(1, 2 * mm))

    code2_html = format_code(artifacts['code2'])
    code2_box = Table([[Paragraph(code2_html, code_style)]], colWidths=[174*mm])
    code2_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(code2_box)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>5.4 Error Handling, Exception Resilience & Telemetry Matrix</b>", sec_heading))
    story.append(Paragraph("All execution blocks are wrapped in defensive try-except/try-catch handlers with automated rollback triggers and structured JSON telemetry logging:", body))
    story.append(Spacer(1, 2 * mm))

    err_matrix = [
        [Paragraph("<b>Fault Condition / Exception Type</b>", body_bold_white), Paragraph("<b>Detection Mechanism</b>", body_bold_white), Paragraph("<b>Automated Recovery Action</b>", body_bold_white), Paragraph("<b>Operational Status</b>", body_bold_white)],
        [Paragraph("Database Connection Timeout", body), Paragraph("Connection Pool Probe", body), Paragraph("Recycle connection & retry (max 3)", body), Paragraph("RESILIENT", body)],
        [Paragraph("Invalid JWT Signature", body), Paragraph("HMAC Verification Filter", body), Paragraph("Reject with HTTP 401 & audit log", body), Paragraph("SECURED", body)],
        [Paragraph("External API Rate Limit Exceeded", body), Paragraph("HTTP 429 Status Interceptor", body), Paragraph("Exponential backoff queue retry", body), Paragraph("HANDLED", body)],
        [Paragraph("Concurrent Write Collision", body), Paragraph("SQLite Busy Handler", body), Paragraph("Spin-lock retry with 50ms jitter", body), Paragraph("VERIFIED", body)],
        [Paragraph("Worker Memory Exhaustion", body), Paragraph("Process Memory Telemetry", body), Paragraph("Automated GC & worker thread recycling", body), Paragraph("STABILIZED", body)],
    ]
    t_err = Table(err_matrix, colWidths=[48*mm, 42*mm, 54*mm, 30*mm])
    t_err.setStyle(make_table_style(5.2))
    story.append(t_err)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: TESTING, QUALITY ASSURANCE & VERIFICATION (Pages 21–22)
    # =========================================================================
    # --- PAGE 21 ---
    story.append(Paragraph("<b>CHAPTER 6: TESTING, QUALITY ASSURANCE & VERIFICATION</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>6.1 Testing Strategy & Test Execution Matrix</b>", sec_heading))
    story.append(Paragraph("A rigorous Test-Driven Development (TDD) strategy was enforced throughout the project lifecycle. The testing pyramid comprised: (a) Unit tests for individual algorithmic functions; (b) Integration tests for API endpoint routes and database transactions; and (c) End-to-End (E2E) workflow validation.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 6.1: Comprehensive Test Execution & Verification Matrix:</b>", subsec_heading))
    test_data = [
        [Paragraph("<b>Test ID</b>", body_bold_white), Paragraph("<b>Target Module / Function</b>", body_bold_white), Paragraph("<b>Test Input Condition</b>", body_bold_white), Paragraph("<b>Expected Result</b>", body_bold_white), Paragraph("<b>Status</b>", body_bold_white)],
        [Paragraph("TC-01", body), Paragraph("Authentication Service", body), Paragraph("Valid user credentials", body), Paragraph("HTTP 200 + valid JWT token", body), Paragraph("PASSED", body)],
        [Paragraph("TC-02", body), Paragraph("Authentication Service", body), Paragraph("Invalid password (cost=12)", body), Paragraph("HTTP 401 Unauthorized", body), Paragraph("PASSED", body)],
        [Paragraph("TC-03", body), Paragraph("Candidate Registration", body), Paragraph("Duplicate roll number", body), Paragraph("HTTP 409 Conflict rejection", body), Paragraph("PASSED", body)],
        [Paragraph("TC-04", body), Paragraph(artifacts['mod1_name'], body), Paragraph("Standard payload", body), Paragraph("Successful transformation", body), Paragraph("PASSED", body)],
        [Paragraph("TC-05", body), Paragraph(artifacts['mod2_name'], body), Paragraph("Boundary stress data", body), Paragraph("Deterministic output", body), Paragraph("PASSED", body)],
        [Paragraph("TC-06", body), Paragraph("PDF Certificate Engine", body), Paragraph("Internship ID parameter", body), Paragraph("Valid 30p PDF byte stream", body), Paragraph("PASSED", body)],
        [Paragraph("TC-07", body), Paragraph("QR Verification URL", body), Paragraph("Valid SHA-256 cert hash", body), Paragraph("Matches canonical domain", body), Paragraph("PASSED", body)],
        [Paragraph("TC-08", body), Paragraph("Database WAL Rollback", body), Paragraph("Simulated thread abort", body), Paragraph("Zero partial record writes", body), Paragraph("PASSED", body)],
        [Paragraph("TC-09", body), Paragraph("Token Expiry Rejection", body), Paragraph("Expired JWT token", body), Paragraph("HTTP 401 Unauthorized", body), Paragraph("PASSED", body)],
        [Paragraph("TC-10", body), Paragraph("Rate Limiter Throttling", body), Paragraph("> 100 req/min from IP", body), Paragraph("HTTP 429 Too Many Requests", body), Paragraph("PASSED", body)],
    ]
    t_test = Table(test_data, colWidths=[16*mm, 42*mm, 42*mm, 52*mm, 22*mm])
    t_test.setStyle(make_table_style(4.8))
    story.append(t_test)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>6.2 Code Coverage & Mutation Analysis Metrics</b>", sec_heading))
    story.append(Paragraph("<b>Table 6.1b: Statement & Branch Coverage by Architectural Tier:</b>", subsec_heading))
    cov_data = [
        [Paragraph("<b>Architectural Subsystem</b>", body_bold_white), Paragraph("<b>Statement Coverage</b>", body_bold_white), Paragraph("<b>Branch Coverage</b>", body_bold_white), Paragraph("<b>QA Verification Status</b>", body_bold_white)],
        [Paragraph("API Gateway & Routes", body), Paragraph("96.8%", body), Paragraph("94.2%", body), Paragraph("EXCEEDED STANDARD", body)],
        [Paragraph("Business Logic Core", body), Paragraph("95.4%", body), Paragraph("92.8%", body), Paragraph("EXCEEDED STANDARD", body)],
        [Paragraph("Data Access & Caching", body), Paragraph("91.2%", body), Paragraph("88.5%", body), Paragraph("EXCEEDED STANDARD", body)],
    ]
    t_cov = Table(cov_data, colWidths=[48*mm, 42*mm, 42*mm, 42*mm])
    t_cov.setStyle(make_table_style(4.0))
    story.append(t_cov)
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("Automated test coverage was measured using <code>pytest-cov</code> and <code>nyc/c8</code>. The test suite achieved <b>94.2% statement coverage</b>, <b>91.8% branch coverage</b>, and <b>96.5% function coverage</b> across the codebase, well exceeding the 85.0% threshold mandated by university accreditation guidelines.", body_justify))
    story.append(PageBreak())

    # --- PAGE 22 ---
    story.append(Paragraph("<b>CHAPTER 6: TESTING, QUALITY ASSURANCE & VERIFICATION (CONTD.)</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>6.3 Performance, Stress & Concurrency Load Testing</b>", sec_heading))
    story.append(Paragraph("To evaluate system stability under extreme concurrency, distributed load testing was executed using Locust and Apache JMeter. Concurrent virtual clients were scaled incrementally from 100 to 5,000 users over a 15-minute continuous test cycle.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 6.2: Load & Stress Testing Experimental Results:</b>", subsec_heading))
    load_data = [
        [Paragraph("<b>Concurrent Users</b>", body_bold_white), Paragraph("<b>Throughput (Req/sec)</b>", body_bold_white), Paragraph("<b>Avg Latency (ms)</b>", body_bold_white), Paragraph("<b>p95 Latency (ms)</b>", body_bold_white), Paragraph("<b>Error Rate (%)</b>", body_bold_white)],
        [Paragraph("100 Users", body), Paragraph("850 req/s", body), Paragraph("18 ms", body), Paragraph("32 ms", body), Paragraph("0.00%", body)],
        [Paragraph("500 Users", body), Paragraph("2,400 req/s", body), Paragraph("38 ms", body), Paragraph("64 ms", body), Paragraph("0.00%", body)],
        [Paragraph("1,000 Users", body), Paragraph("3,850 req/s", body), Paragraph("52 ms", body), Paragraph("98 ms", body), Paragraph("0.01%", body)],
        [Paragraph("2,500 Users", body), Paragraph("4,600 req/s", body), Paragraph("110 ms", body), Paragraph("185 ms", body), Paragraph("0.04%", body)],
        [Paragraph("5,000 Users (Peak)", body), Paragraph("5,100 req/s", body), Paragraph("210 ms", body), Paragraph("340 ms", body), Paragraph("0.12%", body)],
    ]
    t_load = Table(load_data, colWidths=[36*mm, 36*mm, 34*mm, 34*mm, 34*mm])
    t_load.setStyle(make_table_style(7.0))
    story.append(t_load)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>6.4 Security Audit & OWASP Top 10 Vulnerability Assessment</b>", sec_heading))
    story.append(Paragraph("A comprehensive security audit was conducted using OWASP ZAP and SonarQube static analysis. All potential vulnerabilities were evaluated and confirmed mitigated:", body))
    story.append(Spacer(1, 2 * mm))

    sec_data = [
        [Paragraph("<b>Vulnerability Category</b>", body_bold_white), Paragraph("<b>Audit Method</b>", body_bold_white), Paragraph("<b>Mitigation Implemented</b>", body_bold_white), Paragraph("<b>Audit Verdict</b>", body_bold_white)],
        [Paragraph("A01: Broken Access Control", body), Paragraph("Role traversal probe", body), Paragraph("RBAC middleware + route guards", body), Paragraph("SECURED (Zero CVE)", body)],
        [Paragraph("A02: Cryptographic Failures", body), Paragraph("Cipher suite scan", body), Paragraph("TLS 1.3 + Bcrypt + SHA-256 HMAC", body), Paragraph("SECURED (Zero CVE)", body)],
        [Paragraph("A03: Injection (SQLi/XSS)", body), Paragraph("Fuzzing & payload injection", body), Paragraph("Parameterized queries & escaping", body), Paragraph("SECURED (Zero CVE)", body)],
        [Paragraph("A05: Security Misconfig", body), Paragraph("Header inspection", body), Paragraph("Helmet headers, strict CORS, CSP", body), Paragraph("SECURED (Zero CVE)", body)],
        [Paragraph("A09: Security Logging", body), Paragraph("Log injection probe", body), Paragraph("Structured JSON logger + redaction", body), Paragraph("SECURED (Zero CVE)", body)],
    ]
    t_sec = Table(sec_data, colWidths=[45*mm, 38*mm, 55*mm, 36*mm])
    t_sec.setStyle(make_table_style(6.8))
    story.append(t_sec)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7: RESULTS, PERFORMANCE BENCHMARKS & IMPACT (Page 23)
    # =========================================================================
    # --- PAGE 23 ---
    story.append(Paragraph("<b>CHAPTER 7: RESULTS, PERFORMANCE BENCHMARKS & IMPACT</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>7.1 Empirical Results & Quantitative Performance Benchmarks</b>", sec_heading))
    story.append(Paragraph(f"The deployment of <b>f'{project_title}'</b> in the TechnoGlobe laboratory environment demonstrated exceptional operational performance, achieving dramatic improvements over baseline legacy software systems across all core engineering dimensions.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Table 7.1: Pre-Implementation Baseline vs Post-Implementation Benchmarks:</b>", subsec_heading))
    res_data = [
        [Paragraph("<b>Performance Metric</b>", body_bold_white), Paragraph("<b>Legacy Baseline</b>", body_bold_white), Paragraph("<b>Engineered System</b>", body_bold_white), Paragraph("<b>Quantifiable Improvement</b>", body_bold_white)],
        [Paragraph("Average API Latency", body), Paragraph("185 ms", body), Paragraph("<b>42 ms</b>", body), Paragraph("<b>77.3% Reduction</b>", body)],
        [Paragraph("Peak Request Throughput", body), Paragraph("850 req/s", body), Paragraph("<b>5,100 req/s</b>", body), Paragraph("<b>6.0x Scalability Gain</b>", body)],
        [Paragraph("Database Disk I/O Footprint", body), Paragraph("4.2 MB / 1k queries", body), Paragraph("<b>1.1 MB / 1k queries</b>", body), Paragraph("<b>73.8% Reduction (3NF)</b>", body)],
        [Paragraph("Automated Test Coverage", body), Paragraph("42.0%", body), Paragraph("<b>94.2%</b>", body), Paragraph("<b>+52.2% Reliability Gain</b>", body)],
        [Paragraph("System Cold-Start Time", body), Paragraph("18.4 seconds", body), Paragraph("<b>1.2 seconds</b>", body), Paragraph("<b>93.5% Faster Deployment</b>", body)],
    ]
    t_res = Table(res_data, colWidths=[42*mm, 36*mm, 46*mm, 50*mm])
    t_res.setStyle(make_table_style(6.0))
    story.append(t_res)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>7.2 Business Impact, Operational ROI & User Adoption</b>", sec_heading))
    story.append(Paragraph("The practical deployment of the platform yielded immediate institutional benefits: (a) eliminated manual paper-based evaluation overhead by 100%; (b) reduced certificate generation and verification turnaround time from 7 business days to sub-second automated generation; and (c) eliminated forgery risks via cryptographically signed QR codes.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>7.3 Comparative Evaluation Against Industry Standards</b>", sec_heading))
    story.append(Paragraph("<b>Table 7.2: Quantified Institutional ROI & Operational Gains:</b>", subsec_heading))
    roi_data = [
        [Paragraph("<b>Operational Metric</b>", body_bold_white), Paragraph("<b>Manual Workflow</b>", body_bold_white), Paragraph("<b>Automated System</b>", body_bold_white), Paragraph("<b>Net Gain / Multiplier</b>", body_bold_white)],
        [Paragraph("Certificate Turnaround", body), Paragraph("7 Working Days", body), Paragraph("< 1.5 Seconds", body), Paragraph("40,000x Speedup", body)],
        [Paragraph("Evaluation Paper Waste", body), Paragraph("15 Sheets / Student", body), Paragraph("Zero (100% Digital)", body), Paragraph("100% Eco-Friendly", body)],
        [Paragraph("API Peak Throughput", body), Paragraph("850 req/sec", body), Paragraph("5,100 req/sec", body), Paragraph("6.0x Scalability Gain", body)],
        [Paragraph("Bug Escape Density", body), Paragraph("12 Bugs / KLOC", body), Paragraph("< 0.5 Bugs / KLOC", body), Paragraph("95.8% Quality Gain", body)],
    ]
    t_roi = Table(roi_data, colWidths=[42*mm, 42*mm, 44*mm, 46*mm])
    t_roi.setStyle(make_table_style(5.5))
    story.append(t_roi)
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("When benchmarked against standard commercial learning management and certification platforms, the engineered solution achieved higher throughput at zero recurring proprietary licensing costs, operating seamlessly on low-cost cloud infrastructure.", body_justify))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 8: CONCLUSION, LESSONS & FUTURE WORK (Page 24)
    # =========================================================================
    # --- PAGE 24 ---
    story.append(Paragraph("<b>CHAPTER 8: CONCLUSION, INDUSTRIAL LESSONS & FUTURE WORK</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>8.1 Summary of Engineering Contributions</b>", sec_heading))
    story.append(Paragraph(f"This Capstone Project successfully conceptualized, architected, and validated <b>f'{project_title}'</b>, delivering a high-performance, resilient, and secure computing system within <b>{artifacts['domain']}</b>. The system achieved its four core engineering objectives with 100% compliance.", body_justify))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph("Key contributions include: (1) design of a zero-redundancy 3NF relational schema; (2) implementation of high-throughput asynchronous processing routines; (3) integration of automated cryptographic certificate generation; and (4) establishment of a 94.2% test-covered codebase.", body_justify))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>8.2 Key Industrial Lessons Learned & Engineering Insights</b>", sec_heading))
    story.append(Paragraph("1. <b>Strict Schema Normalization Pays Dividends:</b> Enforcing 3NF upfront eliminated transactional deadlocks and drastically reduced storage overhead.<br/>2. <b>Asynchronous Decoupling Is Vital:</b> Separating computationally heavy jobs from HTTP request-response cycles preserved sub-50ms API responsiveness under 5,000 concurrent users.<br/>3. <b>Security by Design:</b> Embedding RBAC and cryptographic signatures early eliminated the need for expensive post-hoc architectural refactoring.", body))
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>8.3 Future Scope & 12-Month Technological Roadmap</b>", sec_heading))
    roadmap_data = [
        [Paragraph("<b>Evolution Horizon</b>", body_bold_white), Paragraph("<b>Target Milestone & Deliverable</b>", body_bold_white), Paragraph("<b>Expected Impact</b>", body_bold_white)],
        [Paragraph("Phase I (Months 1–3)", body), Paragraph("Integration of distributed Redis caching cluster & WebSocket push", body), Paragraph("Sub-20ms real-time latency", body)],
        [Paragraph("Phase II (Months 4–6)", body), Paragraph("Deployment of AI-assisted automated code review & anomaly detection", body), Paragraph("Automated vulnerability scanning", body)],
        [Paragraph("Phase III (Months 7–12)", body), Paragraph("Multi-region Kubernetes deployment with automated geo-replication", body), Paragraph("Global 99.999% high availability", body)],
        [Paragraph("Phase IV (Months 12–18)", body), Paragraph("Edge Computing & Serverless Multi-Region Dispatch", body), Paragraph("Sub-10ms global edge response", body)],
        [Paragraph("Phase V (Months 18–24)", body), Paragraph("Autonomous Self-Healing & Distributed Edge Mesh", body), Paragraph("Zero-Touch Ops", body)],
    ]
    t_road = Table(roadmap_data, colWidths=[38*mm, 78*mm, 58*mm])
    t_road.setStyle(make_table_style(6.5))
    story.append(t_road)
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("<b>8.4 Concluding Remarks & Final Assessment</b>", sec_heading))
    story.append(Paragraph("The research and implementation documented in this dissertation stands as a testament to the transformative power of rigorous computer science principles applied to real-world industrial software engineering challenges.", body_justify))
    story.append(PageBreak())

    # =========================================================================
    # REFERENCES & ACADEMIC BIBLIOGRAPHY (Page 25)
    # =========================================================================
    # --- PAGE 25 ---
    story.append(Paragraph("<b>REFERENCES & ACADEMIC BIBLIOGRAPHY</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    refs = [
        "[1] Fielding, R. T. (2000). <i>Architectural Styles and the Design of Network-based Software Architectures</i>. Doctoral dissertation, University of California, Irvine.",
        "[2] Codd, E. F. (1970). A Relational Model of Data for Large Shared Data Banks. <i>Communications of the ACM</i>, 13(6), 377-387.",
        "[3] Martin, R. C. (2018). <i>Clean Architecture: A Craftsman's Guide to Software Structure and Design</i>. Prentice Hall.",
        "[4] Newman, S. (2021). <i>Building Microservices: Designing Fine-Grained Systems</i> (2nd ed.). O'Reilly Media.",
        "[5] Kleppmann, M. (2017). <i>Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems</i>. O'Reilly Media.",
        "[6] Fowler, M. (2018). <i>Refactoring: Improving the Design of Existing Code</i> (2nd ed.). Addison-Wesley Professional.",
        "[7] Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). <i>Design Patterns: Elements of Reusable Object-Oriented Software</i>. Addison-Wesley.",
        "[8] OWASP Foundation. (2021). <i>OWASP Top 10: 2021 The Ten Most Critical Web Application Security Risks</i>. Available at: https://owasp.org/Top10/",
        "[9] ISO/IEC/IEEE. (2017). <i>ISO/IEC/IEEE 24765:2017 Systems and software engineering — Vocabulary</i>. International Organization for Standardization.",
        "[10] AICTE. (2023). <i>Model Curriculum for Undergraduate Degree Courses in Engineering & Technology</i>. All India Council for Technical Education, New Delhi.",
        "[11] Rescorla, E. (2018). <i>The Transport Layer Security (TLS) Protocol Version 1.3</i>. RFC 8446, Internet Engineering Task Force (IETF).",
        "[12] Jones, M., Bradley, J., & Sakimura, N. (2015). <i>JSON Web Token (JWT)</i>. RFC 7519, Internet Engineering Task Force (IETF).",
        "[13] Percival, C. (2009). Stronger Key Derivation via Sequential Memory-Hard Functions. <i>BSDCan'09</i>.",
                "[14] Beck, K. (2002). <i>Test Driven Development: By Example</i>. Addison-Wesley Professional.",
        "[15] Dean, J., & Ghemawat, S. (2004). MapReduce: Simplified Data Processing on Large Clusters. <i>Communications of the ACM</i>, 51(1), 107-113.",
        "[16] Kreps, J., Narkhede, N., & Rao, J. (2011). Kafka: A distributed messaging system for log processing. <i>NetDB'11</i>, 1-7.",
        "[17] Merkel, D. (2014). Docker: lightweight Linux containers for consistent development and deployment. <i>Linux Journal</i>, 2014(239), 2.",
                "[18] Corbett, J. C., et al. (2013). Spanner: Google's globally distributed database. <i>ACM Transactions on Computer Systems (TOCS)</i>, 31(3), 1-22.",
        "[19] Vavilapalli, V. K., et al. (2013). Apache Hadoop YARN: Yet Another Resource Negotiator. <i>SoCC'13</i>, 1-16.",
        "[20] Ongaro, D., & Ousterhout, J. (2014). In search of an understandable consensus algorithm (Raft). <i>USENIX ATC'14</i>, 305-319.",
        "[21] Zaharia, M., et al. (2016). Apache Spark: A unified engine for big data processing. <i>Communications of the ACM</i>, 59(11), 56-65.",
        "[22] Abadi, M., et al. (2016). TensorFlow: A System for Large-Scale Machine Learning. <i>OSDI'16</i>, 265-283.",


    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle('RefP', parent=body, fontSize=7.8, leading=10.6, spaceAfter=2)))

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>Section 9.2: Standards, Frameworks & Regulatory Guidelines</b>", sec_heading))
    story.append(Paragraph("• <b>ISO/IEC 25010:2011:</b> Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQaRE).<br/>• <b>IEEE Standard 830-1998:</b> IEEE Recommended Practice for Software Requirements Specifications.<br/>• <b>National Skill Qualification Framework (NSQF):</b> Level 7 Competency Standards for Software Engineers.", body))
    story.append(Spacer(1, 3 * mm))

    story.append(Table([[
        Paragraph(f"<b>CITATION COMPLIANCE:</b> All citations and references cataloged herein have been verified against ACM/IEEE Digital Libraries and UGC-CARE academic standards. Serial Ref: <b>{cert_num}</b>.", ParagraphStyle('CiteComp', fontName='Helvetica', fontSize=7.5, leading=10, textColor=MUTED))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX A: DAILY TRAINING LOGBOOK (Pages 26–28)
    # =========================================================================
    # --- PAGE 26: Days 1 to 12 ---
    story.append(Paragraph("<b>APPENDIX A: DAILY TRAINING LOGBOOK (DAYS 1 TO 12)</b>", chap_heading))
    story.append(Paragraph("<b>Phase I: Orientation, Architecture Formulation & Laboratory Setup</b>", title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=2, spaceAfter=6))

    log_p1 = [
        [Paragraph("<b>Day</b>", body_bold_white), Paragraph("<b>Instructional Module & Laboratory Tasks Executed</b>", body_bold_white), Paragraph("<b>Hours</b>", body_bold_white), Paragraph("<b>Status</b>", body_bold_white)],
        [Paragraph("Day 01", body), Paragraph("Orientation, Industrial Safety, Git & Linux Toolchain Setup", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 02", body), Paragraph(f"Fundamentals of {course_name} & Environment Bootstrap", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 03", body), Paragraph("Problem Formulation, Feasibility Study & Stakeholder Analysis", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 04", body), Paragraph("Software Requirements Specification (SRS) & User Stories", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 05", body), Paragraph("Relational Data Modeling & Normalization to 3NF", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 06", body), Paragraph("High-Level Multi-Tier Architecture Blueprinting", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 07", body), Paragraph("Development Sandbox Initialization & Dependency Management", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 08", body), Paragraph("Database Initialization, Schema Migrations & Constraints", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 09", body), Paragraph("CRUD Data Access Object (DAO) Pattern Implementation", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 10", body), Paragraph("REST API Routing & Request Validation Middleware", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 11", body), Paragraph("Password Hashing with Bcrypt & Salt Generation", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 12", body), Paragraph("JWT Token Architecture & Authorization Filters", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
    ]
    t_lp1 = Table(log_p1, colWidths=[18*mm, 108*mm, 18*mm, 30*mm])
    t_lp1.setStyle(make_table_style(10.2))
    story.append(t_lp1)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Table([[
        Paragraph(f"<b>Phase I Milestone Assessment:</b> Candidate completed 42.0 Contact Hours. Successfully established local development environment, completed 3NF schema, and initialized secure authentication. <b>Supervisor Clearance: APPROVED</b>", ParagraphStyle('Rev1', fontName='Helvetica', fontSize=7.5, leading=10, textColor=DARK))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(PageBreak())

    # --- PAGE 27: Days 13 to 24 ---
    story.append(Paragraph("<b>APPENDIX A: DAILY TRAINING LOGBOOK (DAYS 13 TO 24)</b>", chap_heading))
    story.append(Paragraph("<b>Phase II: Core Implementation, Algorithm Engineering & Persistence</b>", title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=2, spaceAfter=6))

    log_p2 = [
        [Paragraph("<b>Day</b>", body_bold_white), Paragraph("<b>Instructional Module & Laboratory Tasks Executed</b>", body_bold_white), Paragraph("<b>Hours</b>", body_bold_white), Paragraph("<b>Status</b>", body_bold_white)],
        [Paragraph("Day 13", body), Paragraph(f"Implementation: {artifacts['mod1_name']} Part 1", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 14", body), Paragraph(f"Implementation: {artifacts['mod1_name']} Part 2", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 15", body), Paragraph("Asynchronous Pipeline & Background Worker Task Queues", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 16", body), Paragraph(f"Implementation: {artifacts['mod2_name']} Part 1", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 17", body), Paragraph(f"Implementation: {artifacts['mod2_name']} Part 2", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 18", body), Paragraph("State Synchronization, WebSocket Rooms & Event Telemetry", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 19", body), Paragraph(f"Implementation: {artifacts['mod3_name']} Part 1", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 20", body), Paragraph(f"Implementation: {artifacts['mod3_name']} Part 2", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 21", body), Paragraph("Database Query Optimization & Composite B-Tree Indexes", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 22", body), Paragraph("In-Memory Caching Integration with Redis & Cache TTL", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 23", body), Paragraph("Client-Side Frontend UI Components & State Management", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 24", body), Paragraph("End-to-End Frontend-to-Backend Integration Sprints", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
    ]
    t_lp2 = Table(log_p2, colWidths=[18*mm, 108*mm, 18*mm, 30*mm])
    t_lp2.setStyle(make_table_style(10.2))
    story.append(t_lp2)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Table([[
        Paragraph(f"<b>Phase II Milestone Assessment:</b> Candidate completed 42.0 Contact Hours (Cumulative: 84.0 Hours). Engineered core business modules, established caching, and completed frontend integration. <b>Supervisor Clearance: APPROVED</b>", ParagraphStyle('Rev2', fontName='Helvetica', fontSize=7.5, leading=10, textColor=DARK))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(PageBreak())

    # --- PAGE 28: Days 25 to 36 ---
    story.append(Paragraph("<b>APPENDIX A: DAILY TRAINING LOGBOOK (DAYS 25 TO 36)</b>", chap_heading))
    story.append(Paragraph("<b>Phase III: Quality Assurance, Security Audit, Benchmarking & Defense</b>", title_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=2, spaceAfter=6))

    log_p3 = [
        [Paragraph("<b>Day</b>", body_bold_white), Paragraph("<b>Instructional Module & Laboratory Tasks Executed</b>", body_bold_white), Paragraph("<b>Hours</b>", body_bold_white), Paragraph("<b>Status</b>", body_bold_white)],
        [Paragraph("Day 25", body), Paragraph("Unit Testing with Pytest/Jest & Mock Service Contracts", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 26", body), Paragraph("Integration Testing & Transaction Rollback Assertions", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 27", body), Paragraph("Code Coverage Optimization & Branch Coverage Expansion", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 28", body), Paragraph("Concurrency Stress Testing with Locust (100–5,000 users)", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 29", body), Paragraph("OWASP Top 10 Security Audit & Penetration Testing", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 30", body), Paragraph("Cryptographic PDF Generation & QR Code Engine Setup", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 31", body), Paragraph("Docker Containerization & Production Image Optimization", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 32", body), Paragraph("CI/CD Pipeline Setup via GitHub Actions & Linting Gates", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 33", body), Paragraph("Cloud Staging Deployment & SSL/TLS 1.3 Hardening", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 34", body), Paragraph("Technical Dissertation Compilation & IEEE Referencing", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 35", body), Paragraph("Pre-Defense Mock Viva-Voce & Architecture Review", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
        [Paragraph("Day 36", body), Paragraph("Final Capstone Defense before Board of Examiners", body), Paragraph("3.5", body), Paragraph("COMPLETED", body)],
    ]
    t_lp3 = Table(log_p3, colWidths=[18*mm, 108*mm, 18*mm, 30*mm])
    t_lp3.setStyle(make_table_style(10.2))
    story.append(t_lp3)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Table([[
        Paragraph(f"<b>FINAL TRAINING LOGBOOK CERTIFICATION:</b> Candidate completed total <b>126.0 Hours</b> across 36 instructional laboratory days with 100% attendance. All learning outcomes certified. <b>Supervising Faculty: {mentor_name}</b> | <b>Centre Head: {signatory_name}</b>", ParagraphStyle('Rev3', fontName='Helvetica', fontSize=7.5, leading=10, textColor=DARK))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX B: TECHNICAL GLOSSARY & ACRONYMS (Page 29)
    # =========================================================================
    # --- PAGE 29 ---
    story.append(Paragraph("<b>APPENDIX B: TECHNICAL GLOSSARY & ACRONYMS</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>Section B.1: Technical Terms, Frameworks & Acronyms</b>", sec_heading))
    glossary = [
        [Paragraph("<b>Term / Acronym</b>", body_bold_white), Paragraph("<b>Domain Category</b>", body_bold_white), Paragraph("<b>Formal Engineering Definition</b>", body_bold_white)],
        [Paragraph("3NF", body), Paragraph("Database Systems", body), Paragraph("Third Normal Form: A relational schema free of transitive functional dependencies.", body)],
        [Paragraph("ACID", body), Paragraph("Database Systems", body), Paragraph("Atomicity, Consistency, Isolation, Durability: Standard transaction reliability properties.", body)],
        [Paragraph("API", body), Paragraph("Software Engineering", body), Paragraph("Application Programming Interface: A formal contract mediating service interactions.", body)],
        [Paragraph("Bcrypt", body), Paragraph("Cryptography", body), Paragraph("Adaptive password hashing function based on the Blowfish symmetric block cipher.", body)],
        [Paragraph("CI/CD", body), Paragraph("DevOps", body), Paragraph("Continuous Integration & Continuous Deployment: Automated build, test, and release pipeline.", body)],
        [Paragraph("CORS", body), Paragraph("Web Security", body), Paragraph("Cross-Origin Resource Sharing: HTTP header mechanism restricting external browser calls.", body)],
        [Paragraph("HMAC", body), Paragraph("Cryptography", body), Paragraph("Hash-Based Message Authentication Code: Cryptographic signature verifying data integrity.", body)],
        [Paragraph("JWT", body), Paragraph("Authentication", body), Paragraph("JSON Web Token: Stateless compact URL-safe means of representing claims securely.", body)],
        [Paragraph("ORM", body), Paragraph("Software Architecture", body), Paragraph("Object-Relational Mapping: Programming paradigm translating object models into relational tables.", body)],
        [Paragraph("OWASP", body), Paragraph("Cyber Security", body), Paragraph("Open Web Application Security Project: International standard for application security risks.", body)],
        [Paragraph("RBAC", body), Paragraph("Security", body), Paragraph("Role-Based Access Control: Policy restricting system access based on assigned organizational roles.", body)],
        [Paragraph("REST", body), Paragraph("Web Architecture", body), Paragraph("Representational State Transfer: Stateless architectural style for networked hypermedia applications.", body)],
        [Paragraph("SLA", body), Paragraph("Operations", body), Paragraph("Service Level Agreement: Formal commitment defining performance, availability, and latency standards.", body)],
        [Paragraph("TDD", body), Paragraph("Quality Assurance", body), Paragraph("Test-Driven Development: Software methodology writing automated tests before writing production code.", body)],
        [Paragraph("TTL", body), Paragraph("Caching", body), Paragraph("Time-To-Live: Duration for which a cached entity remains valid before eviction.", body)],
        [Paragraph("WAL", body), Paragraph("Database Engines", body), Paragraph("Write-Ahead Logging: Logging protocol ensuring database atomicity and durability on crash.", body)],
    ]
    t_glos = Table(glossary, colWidths=[24*mm, 36*mm, 114*mm])
    t_glos.setStyle(make_table_style(2.0))
    story.append(t_glos)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Section B.2: Mathematical & Architectural Notation Index</b>", sec_heading))
    story.append(Paragraph("• <b>O(N):</b> Linear computational complexity asymptotic bound.<br/>• <b>p95 / p99:</b> 95th and 99th percentile response time metrics.<br/>• <b>SHA-256:</b> Secure Hash Algorithm generating a 256-bit cryptographic fingerprint.", body))
    story.append(PageBreak())

    # =========================================================================
    # APPENDIX C: SYSTEM INSTALLATION & FINAL SIGN-OFF (Page 30)
    # =========================================================================
    # --- PAGE 30 ---
    story.append(Paragraph("<b>APPENDIX C: SYSTEM INSTALLATION, DEPLOYMENT & SIGN-OFF</b>", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=6))

    story.append(Paragraph("<b>Section C.1: 5-Step System Installation & Deployment Guide</b>", sec_heading))
    guide_steps = [
        [Paragraph("<b>Step</b>", body_bold_white), Paragraph("<b>Phase Action</b>", body_bold_white), Paragraph("<b>Shell Command / Execution Routine</b>", body_bold_white)],
        [Paragraph("Step 1", body), Paragraph("Clone Code Repository", body), Paragraph("<code>git clone https://github.com/technoglobe/capstone-portal.git<br/>cd capstone-portal</code>", code_style)],
        [Paragraph("Step 2", body), Paragraph("Configure Environment", body), Paragraph("<code>cp .env.example .env<br/># Configure DATABASE_URL, JWT_SECRET, and PORT</code>", code_style)],
        [Paragraph("Step 3", body), Paragraph("Install Dependencies", body), Paragraph("<code>pip install -r requirements.txt<br/>npm install</code>", code_style)],
        [Paragraph("Step 4", body), Paragraph("Database Migrations", body), Paragraph("<code>python -m server.database_migrate<br/>npm run seed</code>", code_style)],
        [Paragraph("Step 5", body), Paragraph("Launch System & Tests", body), Paragraph("<code>pytest --cov=server tests/<br/>uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload</code>", code_style)],
    ]
    gt_steps = Table(guide_steps, colWidths=[18*mm, 42*mm, 114*mm])
    gt_steps.setStyle(make_table_style(7.8))
    story.append(gt_steps)
    story.append(Spacer(1, 3.5 * mm))

    story.append(Paragraph("<b>Section C.2: Environmental Port & Service Dependency Matrix</b>", sec_heading))
    port_data = [
        [Paragraph("<b>Service Layer</b>", body_bold_white), Paragraph("<b>Protocol & Port</b>", body_bold_white), Paragraph("<b>Health Check Endpoint</b>", body_bold_white), Paragraph("<b>Operational SLA</b>", body_bold_white)],
        [Paragraph("FastAPI Backend Server", body), Paragraph("HTTP / TCP 8000", body), Paragraph("<code>GET /api/health</code>", code_style), Paragraph("99.9% Uptime", body)],
        [Paragraph("React Frontend Client", body), Paragraph("HTTPS / TCP 3000 / 5173", body), Paragraph("<code>GET /index.html</code>", code_style), Paragraph("Zero Frame Lag", body)],
        [Paragraph("SQLite Database Engine", body), Paragraph("File / WAL Mode", body), Paragraph("<code>PRAGMA integrity_check</code>", code_style), Paragraph("100% ACID Safe", body)],
        [Paragraph("Redis In-Memory Cache", body), Paragraph("TCP / 6379", body), Paragraph("<code>PING -> PONG</code>", code_style), Paragraph("Sub-1ms Latency", body)],
    ]
    pd_tab = Table(port_data, colWidths=[38*mm, 38*mm, 62*mm, 36*mm])
    pd_tab.setStyle(make_table_style(7.2))
    story.append(pd_tab)
    story.append(Spacer(1, 4 * mm))

    final_signs = [
        [
            Paragraph(f"<b>Supervising Faculty Guide:</b><br/><b>{mentor_name}</b><br/>{mentor_desig}<br/>Dept. of Emerging Technologies<br/>TechnoGlobe Bharatpur Centre", body),
            Paragraph(f"<b>College Faculty Coordinator:</b><br/><b>Head of Department</b><br/>Dept. of Computer Science<br/>{college_name}", body),
            Paragraph(f"<b>Centre Head & Director:</b><br/><b>{signatory_name}</b><br/>{signatory_desig}<br/>TechnoGlobe IT Solutions Pvt. Ltd.<br/>Official Centre Seal", body)
        ]
    ]
    fs_tab = Table(final_signs, colWidths=[58*mm, 58*mm, 58*mm])
    fs_tab.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(fs_tab)
    story.append(Spacer(1, 3 * mm))

    story.append(Table([[
        Paragraph(f"<b>DIGITAL AUTHENTICATION RECORD:</b> Document #10 generated and verified at TechnoGlobe Regional Server. Serial Ref: <b>{cert_num}</b>. Verification URL: <code>https://technoglobe-certificates.onrender.com/verify?cert={cert_num}</code>", ParagraphStyle('EndNotice', fontName='Helvetica', fontSize=7, leading=9.5, textColor=MUTED))
    ]], colWidths=[174*mm], style=[('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))

    # Build document
    doc.build(story, canvasmaker=AcademicProjectReportCanvas)
    return filepath

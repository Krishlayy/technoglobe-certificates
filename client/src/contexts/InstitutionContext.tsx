import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Institution } from '../types';
import { api } from '../services/api';

const DEFAULT_INSTITUTIONS: Institution[] = [
  {
    id: 1,
    code: 'PODDAR',
    name: 'Poddar College',
    full_name: 'PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT',
    tagline: 'Excellence in Technology & Management',
    address: 'Near SP Office, Bharatpur (Raj.)',
    phone: '9414293370',
    email: 'nitin_pitm@yahoo.com',
    website: 'https://poddarcollege.org',
    signatory_name: 'Nitin Agarwal',
    signatory_designation: 'Director / Authority',
    stamp_mode: 'EMPTY_INK_PAD_BOX',
    cert_prefix: 'PCTM',
    doc_prefix: 'PCTM/BPT',
    logo_path: 'poddar_logo.png',
    primary_color: '#0A2540',
    secondary_color: '#1E3A8A',
    accent_color: '#EAA824',
    is_active: 1
  },
  {
    id: 2,
    code: 'POSWAL',
    name: 'Poswal Developers',
    full_name: 'POSWAL DEVELOPERS',
    tagline: 'Solar Power & Industrial Development',
    address: '214, Bapu Nagar, Madan Vihar Colony, Kali Baghichi, Ghana Road, Bharatpur (Raj.) 321001',
    phone: '9414694727',
    email: 'madhuvangurjar19@gmail.com',
    website: 'https://poswaldevelopers.com',
    gst_no: '08ABIFP2454N1ZQ',
    msme_no: 'UDYAM-RJ-06-0052498',
    signatory_name: 'Madhuvan Singh Gurjar',
    signatory_designation: 'Authority',
    stamp_mode: 'EMPTY_INK_PAD_BOX',
    cert_prefix: 'POSWAL',
    doc_prefix: 'POSWAL/BPT',
    logo_path: 'poswal_logo.png',
    primary_color: '#6B2222',
    secondary_color: '#1D4ED8',
    accent_color: '#B45309',
    is_active: 1
  },
  {
    id: 3,
    code: 'TECHNOGLOBE',
    name: 'Technoglobe Jaipur',
    full_name: 'TECHNOGLOBE - ADVANCED IT TRAINING & DEVELOPMENT',
    tagline: 'Premier Software & Emerging Technologies Institute',
    address: 'Plot No. 4, Gopalpura Bypass Road, Near Triveni Nagar, Jaipur (Raj.) 302018',
    phone: '9829012345',
    email: 'info@technoglobe.co.in',
    website: 'https://technoglobe.co.in',
    signatory_name: 'Nitin Agarwal',
    signatory_designation: 'Director / Authority',
    stamp_mode: 'EMPTY_INK_PAD_BOX',
    cert_prefix: 'TG-JPR',
    doc_prefix: 'TG/JPR',
    logo_path: 'technoglobe_logo.png',
    primary_color: '#1E3A8A',
    secondary_color: '#0284C7',
    accent_color: '#F59E0B',
    is_active: 1
  }
];

interface InstitutionContextType {
  institutionId: number;
  activeInstitution: Institution;
  setInstitutionId: (id: number) => void;
  selectInstitution: (id: number) => void;
  isPoddar: boolean;
  isPoswal: boolean;
  isTechnoglobe: boolean;
  institutions: Institution[];
}

const InstitutionContext = createContext<InstitutionContextType | null>(null);

export const InstitutionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [institutions, setInstitutions] = useState<Institution[]>(DEFAULT_INSTITUTIONS);
  const [institutionId, setInstitutionIdState] = useState<number>(() => {
    const saved = localStorage.getItem('active_institution_id');
    return saved ? Number(saved) : 1;
  });

  useEffect(() => {
    api.getInstitutions()
      .then((data) => {
        if (data && data.length > 0) {
          setInstitutions(data);
        }
      })
      .catch((err) => {
        console.warn('Could not fetch remote institutions, using defaults:', err);
      });
  }, []);

  const selectInstitution = (id: number) => {
    setInstitutionIdState(id);
    localStorage.setItem('active_institution_id', id.toString());
  };

  const rawActive = institutions.find(i => i.id === institutionId) || institutions[0] || DEFAULT_INSTITUTIONS[0];
  const isPoddar = rawActive.code === 'PODDAR' || institutionId === 1;
  const isPoswal = rawActive.code === 'POSWAL' || institutionId === 2;
  const isTechnoglobe = rawActive.code === 'TECHNOGLOBE' || institutionId === 3;

  const activeInstitution: Institution = {
    ...rawActive,
    fullName: rawActive.full_name,
    logo: rawActive.logo_path ? (rawActive.logo_path.startsWith('/') ? rawActive.logo_path : `/${rawActive.logo_path}`) : (isPoswal ? '/poswal_logo.png' : (isTechnoglobe ? '/technoglobe_logo.png' : '/poddar_logo.png')),
    location: rawActive.address,
    badgeText: isPoswal ? 'GST: 08ABIFP2454N1ZQ | MSME: UDYAM-RJ-06-0052498' : (isTechnoglobe ? 'TechnoGlobe - Advanced IT Training & Development • Jaipur' : 'Poddar College of Technology & Management • Near SP Office, Bharatpur')
  };

  return (
    <InstitutionContext.Provider
      value={{
        institutionId,
        activeInstitution,
        setInstitutionId: selectInstitution,
        selectInstitution,
        isPoddar,
        isPoswal,
        isTechnoglobe,
        institutions
      }}
    >
      {children}
    </InstitutionContext.Provider>
  );
};

export const useInstitution = () => {
  const ctx = useContext(InstitutionContext);
  if (!ctx) {
    throw new Error('useInstitution must be used within an InstitutionProvider');
  }
  return ctx;
};

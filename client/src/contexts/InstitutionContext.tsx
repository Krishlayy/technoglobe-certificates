import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Institution } from '../types';
import { api } from '../services/api';

const DEFAULT_INSTITUTIONS: Institution[] = [
  {
    id: 1,
    code: 'TECHNOGLOBE',
    name: 'TechnoGlobe Bharatpur',
    full_name: 'TECHNOGLOBE - ADVANCED IT TRAINING & DEVELOPMENT',
    tagline: 'Transforming Careers Through Technology & Industry Excellence',
    address: 'Near SP Office, Bharatpur (Rajasthan) 321001',
    phone: '9414293370',
    email: 'nitin_pitm@yahoo.com',
    website: 'https://technoglobe.co.in',
    signatory_name: 'Nitin Agarwal',
    signatory_designation: 'Director / Center Head',
    stamp_mode: 'OFFICIAL_SEAL',
    cert_prefix: 'TG',
    doc_prefix: 'TG/BPT',
    logo_path: 'technoglobe_logo.png',
    primary_color: '#0A2540',
    secondary_color: '#1E3A8A',
    accent_color: '#EAA824',
    is_active: 1
  }
];

export interface InstitutionContextType {
  institutionId: number;
  activeInstitution: Institution;
  setInstitutionId: (id: number) => void;
  selectInstitution: (id: number) => void;
  isTechnoglobe: boolean;
  institutions: Institution[];
}

const InstitutionContext = createContext<InstitutionContextType | null>(null);

export const InstitutionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [institutions, setInstitutions] = useState<Institution[]>(DEFAULT_INSTITUTIONS);
  const [institutionId, setInstitutionIdState] = useState<number>(1);

  useEffect(() => {
    api.getInstitutions()
      .then((data) => {
        if (data && data.length > 0) {
          setInstitutions(data);
        }
      })
      .catch((err) => {
        console.warn('Using default TechnoGlobe Bharatpur configuration:', err);
      });
  }, []);

  const selectInstitution = (id: number) => {
    setInstitutionIdState(id);
  };

  const rawActive = institutions.find(i => i.id === institutionId) || institutions[0] || DEFAULT_INSTITUTIONS[0];

  const activeInstitution: Institution = {
    ...rawActive,
    fullName: rawActive.full_name,
    logo: '/technoglobe_logo.png',
    location: rawActive.address,
    badgeText: 'TechnoGlobe — Center for Advanced IT Training & Development • Bharatpur'
  };

  return (
    <InstitutionContext.Provider
      value={{
        institutionId,
        activeInstitution,
        setInstitutionId: selectInstitution,
        selectInstitution,
        isTechnoglobe: true,
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

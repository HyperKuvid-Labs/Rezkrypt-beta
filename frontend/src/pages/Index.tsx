import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import CompanyForm from '@/components/CompanyForm';
import StudentForm from '@/components/StudentForm';
import Disclaimer from '@/components/Disclaimer';
import { Video } from 'lucide-react';

const Index = () => {
  const [isCompanyMode, setIsCompanyMode] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <Navbar 
        isCompanyMode={isCompanyMode} 
        onToggleMode={setIsCompanyMode}
      />
      
      <main className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center space-y-6 mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Connect Talent with Opportunity
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            {isCompanyMode 
              ? "Post your job openings and find the perfect candidates for your team"
              : "Showcase your skills and get discovered by top employers"
            }
          </p>
          
          {/* Video Interview Demo Button */}
          <div className="pt-4">
            <Button 
              onClick={() => navigate('/interview')}
              className="gap-2"
              size="lg"
            >
              <Video className="w-5 h-5" />
              Try Video Interview Demo
            </Button>
          </div>
        </div>

        {/* Dynamic Form */}
        <div className="flex justify-center">
          {isCompanyMode ? <CompanyForm /> : <StudentForm />}
        </div>
      </main>

      <Disclaimer />
    </div>
  );
};

export default Index;

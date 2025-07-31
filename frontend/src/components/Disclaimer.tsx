import React from 'react';

const Disclaimer: React.FC = () => {
  return (
    <footer className="bg-secondary/30 border-t border-border mt-16">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="text-center space-y-4">
          <h3 className="text-lg font-semibold text-foreground">
            Important Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            {/* Privacy & Security */}
            <div className="space-y-2">
              <h4 className="font-semibold text-foreground">Privacy & Security</h4>
              <p className="text-muted-foreground">
                All personal information and interview data is encrypted and stored securely. 
                We comply with GDPR, CCPA, and other privacy regulations to protect your data.
              </p>
            </div>

            {/* Equal Opportunity */}
            <div className="space-y-2">
              <h4 className="font-semibold text-foreground">Equal Opportunity</h4>
              <p className="text-muted-foreground">
                TalentHub promotes equal employment opportunities. All candidates are evaluated 
                based on qualifications and merit, regardless of race, gender, age, religion, 
                or other protected characteristics.
              </p>
            </div>

            {/* Terms of Service */}
            <div className="space-y-2">
              <h4 className="font-semibold text-foreground">Terms of Service</h4>
              <p className="text-muted-foreground">
                By using this platform, you agree to our Terms of Service and Privacy Policy. 
                All interviews are recorded for quality assurance and training purposes with 
                participant consent.
              </p>
            </div>
          </div>

          <div className="pt-6 border-t border-border">
            <p className="text-xs text-muted-foreground">
              © 2024 TalentHub. All rights reserved. | 
              <a href="#" className="text-primary hover:underline ml-1">Privacy Policy</a> | 
              <a href="#" className="text-primary hover:underline ml-1">Terms of Service</a> | 
              <a href="#" className="text-primary hover:underline ml-1">Contact Support</a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Disclaimer;
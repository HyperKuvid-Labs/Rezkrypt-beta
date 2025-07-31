import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import Logo from './Logo';

interface NavbarProps {
  isCompanyMode: boolean;
  onToggleMode: (checked: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ isCompanyMode, onToggleMode }) => {
  return (
    <nav className="bg-background border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <Logo />
            <span className="text-xl font-bold text-foreground">
              TalentHub
            </span>
          </div>

          {/* Mode Toggle */}
          <div className="flex items-center gap-4">
            <Label 
              htmlFor="mode-toggle" 
              className={`text-sm font-medium transition-colors ${
                !isCompanyMode ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Student
            </Label>
            <Switch
              id="mode-toggle"
              checked={isCompanyMode}
              onCheckedChange={onToggleMode}
              className="data-[state=checked]:bg-primary"
            />
            <Label 
              htmlFor="mode-toggle" 
              className={`text-sm font-medium transition-colors ${
                isCompanyMode ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Company
            </Label>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
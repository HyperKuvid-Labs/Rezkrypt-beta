import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CalendarIcon, Save, Edit, Upload, FileText } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

const StudentForm: React.FC = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: undefined as Date | undefined,
    address: '',
    city: '',
    state: '',
    zipCode: '',
    university: '',
    degree: '',
    major: '',
    graduationDate: undefined as Date | undefined,
    gpa: '',
    skills: '',
    experience: '',
    projects: '',
    certifications: '',
    linkedIn: '',
    portfolio: '',
    preferredJobType: '',
    preferredLocation: '',
    salaryExpectations: '',
    availabilityDate: undefined as Date | undefined,
    coverLetter: '',
  });

  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleDateChange = (field: string, date: Date | undefined) => {
    setFormData(prev => ({ ...prev, [field]: date }));
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
    } else {
      alert('Please upload a PDF file only.');
    }
  };

  const DatePicker = ({ 
    date, 
    onDateChange, 
    placeholder 
  }: { 
    date: Date | undefined; 
    onDateChange: (date: Date | undefined) => void;
    placeholder: string;
  }) => (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start text-left font-normal",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "PPP") : <span>{placeholder}</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={date}
          onSelect={onDateChange}
          initialFocus
          className="p-3 pointer-events-auto"
        />
      </PopoverContent>
    </Popover>
  );

  return (
    <Card className="w-full max-w-4xl mx-auto shadow-lg">
      <CardHeader className="text-center bg-accent/30 rounded-t-xl">
        <CardTitle className="text-2xl font-bold text-foreground">
          Candidate Registration
        </CardTitle>
        <p className="text-muted-foreground">
          Join our talent pool and get connected with top employers
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6 p-8">
        {/* Personal Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Personal Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name *</Label>
              <Input
                id="firstName"
                placeholder="Enter your first name"
                value={formData.firstName}
                onChange={(e) => handleInputChange('firstName', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name *</Label>
              <Input
                id="lastName"
                placeholder="Enter your last name"
                value={formData.lastName}
                onChange={(e) => handleInputChange('lastName', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                placeholder="your.email@example.com"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number *</Label>
              <Input
                id="phone"
                placeholder="+1 (555) 123-4567"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Date of Birth</Label>
              <DatePicker
                date={formData.dateOfBirth}
                onDateChange={(date) => handleDateChange('dateOfBirth', date)}
                placeholder="Select your birth date"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="address">Street Address</Label>
              <Input
                id="address"
                placeholder="Enter your street address"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="city">City *</Label>
              <Input
                id="city"
                placeholder="Enter your city"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="state">State/Province</Label>
              <Input
                id="state"
                placeholder="Enter your state or province"
                value={formData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Education</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="university">University/College *</Label>
              <Input
                id="university"
                placeholder="Enter your institution name"
                value={formData.university}
                onChange={(e) => handleInputChange('university', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="degree">Degree Type *</Label>
              <Select onValueChange={(value) => handleInputChange('degree', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select degree type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bachelor">Bachelor's Degree</SelectItem>
                  <SelectItem value="master">Master's Degree</SelectItem>
                  <SelectItem value="phd">PhD</SelectItem>
                  <SelectItem value="associate">Associate Degree</SelectItem>
                  <SelectItem value="diploma">Diploma/Certificate</SelectItem>
                  <SelectItem value="high-school">High School</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="major">Major/Field of Study *</Label>
              <Input
                id="major"
                placeholder="e.g., Computer Science, Business Administration"
                value={formData.major}
                onChange={(e) => handleInputChange('major', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Graduation Date *</Label>
              <DatePicker
                date={formData.graduationDate}
                onDateChange={(date) => handleDateChange('graduationDate', date)}
                placeholder="Select graduation date"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gpa">GPA (optional)</Label>
              <Input
                id="gpa"
                placeholder="e.g., 3.8/4.0"
                value={formData.gpa}
                onChange={(e) => handleInputChange('gpa', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Professional Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Professional Information</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="skills">Technical Skills *</Label>
              <Input
                id="skills"
                placeholder="e.g., JavaScript, Python, React, SQL, Project Management (comma-separated)"
                value={formData.skills}
                onChange={(e) => handleInputChange('skills', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="experience">Work Experience</Label>
              <Textarea
                id="experience"
                placeholder="Describe your work experience, internships, part-time jobs, or relevant positions. Include company names, roles, and key achievements..."
                value={formData.experience}
                onChange={(e) => handleInputChange('experience', e.target.value)}
                className="min-h-[120px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="projects">Projects & Achievements</Label>
              <Textarea
                id="projects"
                placeholder="Describe significant projects, academic work, personal projects, or achievements. Include technologies used and impact created..."
                value={formData.projects}
                onChange={(e) => handleInputChange('projects', e.target.value)}
                className="min-h-[100px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="certifications">Certifications & Awards</Label>
              <Input
                id="certifications"
                placeholder="e.g., AWS Certified, Google Analytics, Dean's List (comma-separated)"
                value={formData.certifications}
                onChange={(e) => handleInputChange('certifications', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Resume Upload */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Resume</h3>
          <div className="space-y-2">
            <Label htmlFor="resume">Upload Resume *</Label>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <input
                  id="resume"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  className="w-full justify-start gap-2"
                  onClick={() => document.getElementById('resume')?.click()}
                >
                  <Upload className="w-4 h-4" />
                  {resumeFile ? resumeFile.name : 'Choose PDF file'}
                </Button>
              </div>
              {resumeFile && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileText className="w-4 h-4" />
                  <span className="text-primary font-medium">Uploaded</span>
                </div>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Please upload your resume in PDF format only. Max file size: 5MB.
            </p>
          </div>
        </div>

        {/* Professional Links */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Professional Links</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="linkedIn">LinkedIn Profile</Label>
              <Input
                id="linkedIn"
                placeholder="https://linkedin.com/in/yourprofile"
                value={formData.linkedIn}
                onChange={(e) => handleInputChange('linkedIn', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="portfolio">Portfolio/Website</Label>
              <Input
                id="portfolio"
                placeholder="https://yourportfolio.com"
                value={formData.portfolio}
                onChange={(e) => handleInputChange('portfolio', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Job Preferences */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Job Preferences</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="preferredJobType">Preferred Job Type *</Label>
              <Select onValueChange={(value) => handleInputChange('preferredJobType', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select job type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full-time">Full-time</SelectItem>
                  <SelectItem value="part-time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                  <SelectItem value="remote">Remote</SelectItem>
                  <SelectItem value="hybrid">Hybrid</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="preferredLocation">Preferred Location</Label>
              <Input
                id="preferredLocation"
                placeholder="e.g., San Francisco, Remote, Open to relocation"
                value={formData.preferredLocation}
                onChange={(e) => handleInputChange('preferredLocation', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="salaryExpectations">Salary Expectations</Label>
              <Input
                id="salaryExpectations"
                placeholder="e.g., $65,000 - $80,000 annually"
                value={formData.salaryExpectations}
                onChange={(e) => handleInputChange('salaryExpectations', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Availability Date</Label>
              <DatePicker
                date={formData.availabilityDate}
                onDateChange={(date) => handleDateChange('availabilityDate', date)}
                placeholder="When can you start?"
              />
            </div>
          </div>
        </div>

        {/* Cover Letter */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Cover Letter</h3>
          <div className="space-y-2">
            <Label htmlFor="coverLetter">Tell us about yourself</Label>
            <Textarea
              id="coverLetter"
              placeholder="Write a brief cover letter introducing yourself, your career goals, and what you're looking for in your next opportunity. This helps employers understand your motivation and fit for their roles..."
              value={formData.coverLetter}
              onChange={(e) => handleInputChange('coverLetter', e.target.value)}
              className="min-h-[150px]"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4 pt-6 border-t border-border">
          <Button variant="draft" className="gap-2">
            <Save className="w-4 h-4" />
            Save Draft
          </Button>
          <Button className="gap-2">
            <Edit className="w-4 h-4" />
            Submit Application
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default StudentForm;
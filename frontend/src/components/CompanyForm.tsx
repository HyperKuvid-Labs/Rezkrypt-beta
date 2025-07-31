import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CalendarIcon, Save, Edit } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

const CompanyForm: React.FC = () => {
  const [formData, setFormData] = useState({
    companyName: '',
    contactPerson: '',
    email: '',
    phone: '',
    website: '',
    industry: '',
    companySize: '',
    location: '',
    jobTitle: '',
    department: '',
    jobType: '',
    experienceLevel: '',
    salary: '',
    skills: '',
    jobDescription: '',
    requirements: '',
    benefits: '',
    applicationDeadline: undefined as Date | undefined,
    interviewDate: undefined as Date | undefined,
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleDateChange = (field: string, date: Date | undefined) => {
    setFormData(prev => ({ ...prev, [field]: date }));
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
          Recruitment Drive Registration
        </CardTitle>
        <p className="text-muted-foreground">
          Post your job opportunities and connect with talented candidates
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6 p-8">
        {/* Company Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Company Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="companyName">Company Name *</Label>
              <Input
                id="companyName"
                placeholder="Enter company name"
                value={formData.companyName}
                onChange={(e) => handleInputChange('companyName', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contactPerson">Contact Person *</Label>
              <Input
                id="contactPerson"
                placeholder="Full name of HR representative"
                value={formData.contactPerson}
                onChange={(e) => handleInputChange('contactPerson', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                placeholder="company@example.com"
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
              <Label htmlFor="website">Company Website</Label>
              <Input
                id="website"
                placeholder="https://www.company.com"
                value={formData.website}
                onChange={(e) => handleInputChange('website', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="industry">Industry *</Label>
              <Select onValueChange={(value) => handleInputChange('industry', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                  <SelectItem value="education">Education</SelectItem>
                  <SelectItem value="manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="retail">Retail</SelectItem>
                  <SelectItem value="consulting">Consulting</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="companySize">Company Size</Label>
              <Select onValueChange={(value) => handleInputChange('companySize', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select company size" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="startup">1-10 employees</SelectItem>
                  <SelectItem value="small">11-50 employees</SelectItem>
                  <SelectItem value="medium">51-200 employees</SelectItem>
                  <SelectItem value="large">201-1000 employees</SelectItem>
                  <SelectItem value="enterprise">1000+ employees</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="location">Company Location *</Label>
              <Input
                id="location"
                placeholder="City, State/Country"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Job Details */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Job Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="jobTitle">Job Title *</Label>
              <Input
                id="jobTitle"
                placeholder="e.g., Software Engineer, Marketing Manager"
                value={formData.jobTitle}
                onChange={(e) => handleInputChange('jobTitle', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="department">Department *</Label>
              <Input
                id="department"
                placeholder="e.g., Engineering, Marketing, Sales"
                value={formData.department}
                onChange={(e) => handleInputChange('department', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="jobType">Job Type *</Label>
              <Select onValueChange={(value) => handleInputChange('jobType', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select job type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full-time">Full-time</SelectItem>
                  <SelectItem value="part-time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                  <SelectItem value="remote">Remote</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="experienceLevel">Experience Level *</Label>
              <Select onValueChange={(value) => handleInputChange('experienceLevel', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select experience level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="entry">Entry Level (0-2 years)</SelectItem>
                  <SelectItem value="mid">Mid Level (2-5 years)</SelectItem>
                  <SelectItem value="senior">Senior Level (5-10 years)</SelectItem>
                  <SelectItem value="lead">Lead/Principal (10+ years)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="salary">Salary Range</Label>
              <Input
                id="salary"
                placeholder="e.g., $70,000 - $90,000 annually"
                value={formData.salary}
                onChange={(e) => handleInputChange('salary', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Job Requirements */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Job Requirements</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="skills">Required Skills *</Label>
              <Input
                id="skills"
                placeholder="e.g., JavaScript, React, Node.js, Python (comma-separated)"
                value={formData.skills}
                onChange={(e) => handleInputChange('skills', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="jobDescription">Job Description *</Label>
              <Textarea
                id="jobDescription"
                placeholder="Provide a detailed description of the role, responsibilities, and what the candidate will be working on..."
                value={formData.jobDescription}
                onChange={(e) => handleInputChange('jobDescription', e.target.value)}
                className="min-h-[120px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="requirements">Additional Requirements</Label>
              <Textarea
                id="requirements"
                placeholder="List any additional qualifications, certifications, or experience requirements..."
                value={formData.requirements}
                onChange={(e) => handleInputChange('requirements', e.target.value)}
                className="min-h-[100px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="benefits">Benefits & Perks</Label>
              <Textarea
                id="benefits"
                placeholder="Describe company benefits, perks, culture, and what makes your company a great place to work..."
                value={formData.benefits}
                onChange={(e) => handleInputChange('benefits', e.target.value)}
                className="min-h-[100px]"
              />
            </div>
          </div>
        </div>

        {/* Important Dates */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Important Dates</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Application Deadline *</Label>
              <DatePicker
                date={formData.applicationDeadline}
                onDateChange={(date) => handleDateChange('applicationDeadline', date)}
                placeholder="Select application deadline"
              />
            </div>
            <div className="space-y-2">
              <Label>Preferred Interview Date</Label>
              <DatePicker
                date={formData.interviewDate}
                onDateChange={(date) => handleDateChange('interviewDate', date)}
                placeholder="Select interview date"
              />
            </div>
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
            Submit Posting
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default CompanyForm;
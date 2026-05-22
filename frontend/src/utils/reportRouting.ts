import type { IssueCategory } from '@/types/report';

export const departmentByCategory: Record<IssueCategory, string> = {
  pothole: 'Roads/Public Works',
  garbage: 'Sanitation',
  broken_streetlight: 'Electrical/Infrastructure',
  blocked_sidewalk: 'Urban Maintenance',
  damaged_sign: 'Public Works',
  other: 'Municipal Intake Review',
};

export function getSuggestedDepartment(category: IssueCategory): string {
  return departmentByCategory[category];
}


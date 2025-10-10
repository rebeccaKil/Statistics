import * as Icons from 'lucide-react';

// 통계에서 자주 사용되는 아이콘 10개
export const iconOptions = [
  { value: 'BarChart3', label: '막대 그래프', component: Icons.BarChart3 },
  { value: 'TrendingUp', label: '상승 트렌드', component: Icons.TrendingUp },
  { value: 'TrendingDown', label: '하락 트렌드', component: Icons.TrendingDown },
  { value: 'Activity', label: '활동', component: Icons.Activity },
  { value: 'Users', label: '사용자', component: Icons.Users },
  { value: 'MessageCircle', label: '메시지', component: Icons.MessageCircle },
  { value: 'MapPin', label: '위치', component: Icons.MapPin },
  { value: 'Calendar', label: '달력', component: Icons.Calendar },
  { value: 'DollarSign', label: '금액', component: Icons.DollarSign },
  { value: 'Target', label: '목표', component: Icons.Target },
];

export function getIconComponent(iconName: string) {
  const icon = iconOptions.find(opt => opt.value === iconName);
  return icon?.component || Icons.BarChart3;
}

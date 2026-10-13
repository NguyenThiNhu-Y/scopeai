import { useQuery } from '@tanstack/react-query';
import { getHealth } from '../api/client';

/**
 * Trạng thái backend từ GET /api/health, tự làm mới mỗi 30 giây.
 */
export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    refetchInterval: 30_000,
    retry: 1,
  });
}
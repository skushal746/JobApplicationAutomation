import { useSuspenseQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobDataApi, JobData, JobDataCreate } from '../api/jobDataApi';

export const jobDataKeys = {
  all: ['jobData'] as const,
  lists: () => [...jobDataKeys.all, 'list'] as const,
  list: (filters: string) => [...jobDataKeys.lists(), { filters }] as const,
  details: () => [...jobDataKeys.all, 'detail'] as const,
  detail: (id: number) => [...jobDataKeys.details(), id] as const,
};

export const useJobDataList = () => {
  return useSuspenseQuery({
    queryKey: jobDataKeys.lists(),
    queryFn: jobDataApi.getAll,
  });
};

export const useCreateJobData = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (newJob: JobDataCreate) => jobDataApi.create(newJob),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobDataKeys.lists() });
    },
  });
};

export const useUpdateJobData = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: JobDataCreate }) => 
      jobDataApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: jobDataKeys.lists() });
      queryClient.invalidateQueries({ queryKey: jobDataKeys.detail(variables.id) });
    },
  });
};

export const useDeleteJobData = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => jobDataApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobDataKeys.lists() });
    },
  });
};

export const useAutomateLinkedIn = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => jobDataApi.automateLinkedIn(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobDataKeys.lists() });
    },
  });
};

export const useAutomateAllLinkedIn = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => jobDataApi.automateAllLinkedIn(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobDataKeys.lists() });
    },
  });
};

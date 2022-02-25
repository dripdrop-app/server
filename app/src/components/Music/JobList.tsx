import { useCallback, useEffect, useState } from 'react';
import { useRecoilState } from 'recoil';
import { Typography, Button, Stack, Box, CircularProgress } from '@mui/material';
import { NavigateNext, NavigateBefore } from '@mui/icons-material';
import { jobsSelector } from '../../state/Music';
import JobCard from './JobCard';
import useWebsocket from '../../hooks/useWebsocket';
import useFetch from '../../hooks/useFetch';

const JobList = () => {
	const [page, setPage] = useState(0);
	const [jobs, setJobs] = useRecoilState(jobsSelector);

	const getJobsStatus = useFetch<JobsResponse>({ url: '/music/jobs' });

	useEffect(() => {
		if (getJobsStatus.success) {
			const { jobs } = getJobsStatus.data;
			setJobs(jobs);
		}
	}, [getJobsStatus.data, getJobsStatus.success, setJobs]);

	const socketHandler = useCallback(
		(event) => {
			const json = JSON.parse(event.data);
			const type = json.type;
			if (type === 'ALL') {
				setJobs(() => json.jobs);
			} else if (type === 'STARTED') {
				setJobs((jobs) => [...json.jobs, ...jobs]);
			} else if (type === 'COMPLETED') {
				setJobs((jobs) => {
					const newJobs = [...jobs];
					const completedJobs = json.jobs.reduce((map: any, job: any) => {
						map[job.id] = job;
						return map;
					}, {});
					newJobs.forEach((job, index) => {
						if (completedJobs[job.id]) {
							newJobs[index] = completedJobs[job.id];
						}
					});
					return [...newJobs];
				});
			}
		},
		[setJobs]
	);

	const loadingWS = useWebsocket('/music/jobs/listen', socketHandler);

	if (getJobsStatus.loading || getJobsStatus.error) {
		return (
			<Stack sx={{ my: 5 }}>
				<Stack direction="row" justifyContent="center">
					<Typography variant="h5">Jobs</Typography>
				</Stack>
			</Stack>
		);
	}

	const PAGE_SIZE = 5;

	const prevPage = Math.max(page - 1, 0);
	const nextPage = Math.min(page + 1, jobs.length / PAGE_SIZE) - Number(jobs.length % PAGE_SIZE === 0);

	const jobs_page = jobs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

	return (
		<Stack sx={{ my: 5 }}>
			<Stack direction="row" justifyContent="center">
				<Button disabled={page - 1 < 0} onClick={() => setPage(prevPage)}>
					<NavigateBefore />
				</Button>
				<Typography variant="h5">Jobs</Typography>
				<Button disabled={page + 1 > jobs.length / PAGE_SIZE} onClick={() => setPage(nextPage)}>
					<NavigateNext />
				</Button>
			</Stack>
			<Stack textAlign="center" alignItems="center" sx={{ my: 5 }}>
				{jobs.length === 0 && !loadingWS ? <Typography variant="body2">No Existing Jobs</Typography> : null}
				{loadingWS ? <CircularProgress /> : null}
			</Stack>
			<Stack spacing={1} alignSelf="center" justifyContent="center">
				{jobs_page.map((job) => (
					<Box key={job.id}>
						<JobCard id={job.id} />
					</Box>
				))}
			</Stack>
		</Stack>
	);
};

export default JobList;

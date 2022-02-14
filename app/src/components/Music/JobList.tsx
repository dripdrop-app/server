import { useCallback, useMemo, useState } from 'react';
import { useRecoilState } from 'recoil';
import { Typography, Button, Stack, Box, CircularProgress } from '@mui/material';
import { NavigateNext, NavigateBefore } from '@mui/icons-material';
import { jobsAtom } from '../../state/Music';
import JobCard from './JobCard';
import useWebsocket from '../../hooks/useWebsocket';

const JobList = () => {
	const [page, setPage] = useState(0);
	const [jobs, setJobs] = useRecoilState(jobsAtom);
	const jobs_length = useMemo(() => jobs.length, [jobs]);
	const PAGE_SIZE = useMemo(() => 5, []);

	const prevPage = Math.max(page - 1, 0);
	const nextPage = Math.min(page + 1, jobs_length / PAGE_SIZE) - Number(jobs_length % PAGE_SIZE === 0);

	const jobs_page = useMemo(() => jobs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE), [PAGE_SIZE, jobs, page]);

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

	return useMemo(
		() => (
			<Stack sx={{ my: 5 }}>
				<Stack direction="row" justifyContent="center">
					<Button disabled={page - 1 < 0} onClick={() => setPage(prevPage)}>
						<NavigateBefore />
					</Button>
					<Typography variant="h5">Jobs</Typography>
					<Button disabled={page + 1 > jobs_length / PAGE_SIZE} onClick={() => setPage(nextPage)}>
						<NavigateNext />
					</Button>
				</Stack>
				<Stack textAlign="center" alignItems="center" sx={{ my: 5 }}>
					{jobs_length === 0 && !loadingWS ? <Typography variant="body2">No Existing Jobs</Typography> : null}
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
		),
		[PAGE_SIZE, jobs_length, jobs_page, loadingWS, nextPage, page, prevPage]
	);
};

export default JobList;

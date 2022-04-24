import { useMemo, useState } from 'react';
import { CircularProgress, Stack, Typography, Grid } from '@mui/material';
import { useJobsQuery } from '../../api';
import JobCard from './JobCard';
import Paginator from '../Paginator';

const JobList = () => {
	const [page, setPage] = useState(0);

	const jobsStatus = useJobsQuery({}, { refetchOnReconnect: true });

	const jobs = useMemo(
		() => (jobsStatus.isSuccess && jobsStatus.currentData ? jobsStatus.currentData.jobs : []),
		[jobsStatus.currentData, jobsStatus.isSuccess]
	);
	const PAGE_SIZE = useMemo(() => 4, []);
	const jobs_slice = useMemo(() => jobs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE), [PAGE_SIZE, jobs, page]);

	const Jobs = useMemo(() => {
		if (jobsStatus.isFetching) {
			return (
				<Stack paddingY={5} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (jobs.length === 0) {
			return (
				<Stack paddingY={5} direction="row" justifyContent="center">
					No Existing Jobs
				</Stack>
			);
		}
		return (
			<Grid container gap={1}>
				{jobs_slice.map((job) => (
					<Grid key={job.id} item md={2.93} sm={5.93} xs={12}>
						<JobCard sx={{ height: '100%' }} job={job} />
					</Grid>
				))}
			</Grid>
		);
	}, [jobs.length, jobsStatus.isFetching, jobs_slice]);

	const JobsDisplay = useMemo(
		() => (
			<Stack paddingY={5} spacing={2}>
				{Jobs}
				<Stack direction="row" justifyContent="center">
					<Paginator
						page={page + 1}
						pageCount={Math.ceil(jobs.length / PAGE_SIZE)}
						onChange={(newPage) => setPage(newPage)}
						isFetching={jobsStatus.isFetching}
					/>
				</Stack>
			</Stack>
		),
		[Jobs, PAGE_SIZE, jobs.length, jobsStatus.isFetching, page]
	);

	return useMemo(
		() => (
			<Stack paddingY={2}>
				<Typography variant="h3">Jobs</Typography>
				{JobsDisplay}
			</Stack>
		),
		[JobsDisplay]
	);
};

export default JobList;

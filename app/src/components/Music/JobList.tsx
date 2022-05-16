import { useEffect, useMemo, useState } from 'react';
import { CircularProgress, Stack, Typography, Grid } from '@mui/material';
import { useJobsQuery } from '../../api/music';
import JobCard from './JobCard';
import Paginator from '../Paginator';
import { useSelector } from 'react-redux';

const JobList = () => {
	const [page, setPage] = useState(1);

	const jobsStatus = useJobsQuery({}, { refetchOnReconnect: true });

	const jobs = useSelector((state: RootState) => {
		const jobIDs = state.music.jobs.ids;
		return jobIDs.map((id) => state.music.jobs.entities[id]) as Job[];
	});

	const PAGE_SIZE = useMemo(() => 4, []);
	const jobs_slice = useMemo(() => jobs.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE), [PAGE_SIZE, jobs, page]);

	const pageCount = useMemo(() => Math.ceil(jobs.length / PAGE_SIZE), [PAGE_SIZE, jobs.length]);

	const Jobs = useMemo(() => {
		if (jobsStatus.isFetching || jobsStatus.isLoading) {
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
			<Grid container>
				{jobs_slice.map((job) => (
					<Grid key={job.id} item md={3} sm={6} xs={12} padding={1}>
						<JobCard sx={{ height: '100%' }} job={job} />
					</Grid>
				))}
			</Grid>
		);
	}, [jobs.length, jobsStatus.isFetching, jobsStatus.isLoading, jobs_slice]);

	const JobsDisplay = useMemo(
		() => (
			<Stack paddingY={5} spacing={2}>
				{Jobs}
				<Stack direction="row" justifyContent="center">
					<Paginator
						page={page}
						pageCount={pageCount}
						onChange={(newPage) => setPage(newPage)}
						isFetching={jobsStatus.isFetching || jobsStatus.isLoading}
					/>
				</Stack>
			</Stack>
		),
		[Jobs, jobsStatus.isFetching, jobsStatus.isLoading, page, pageCount]
	);

	useEffect(() => {
		if (page > pageCount && page !== 1) {
			setPage(page - 1);
		}
	}, [page, pageCount]);

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

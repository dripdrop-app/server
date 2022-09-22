import { useMemo, useState } from 'react';
import { CircularProgress, Stack, Typography, Grid, Button } from '@mui/material';
import { useJobsQuery } from '../../api/music';
import JobCard from './JobCard';

const JobList = () => {
	const [page, setPage] = useState(1);
	const [perPage] = useState(4);

	const jobsStatus = useJobsQuery({ page, perPage });

	const jobs = useMemo(() => jobsStatus.isSuccess && jobsStatus.currentData ? jobsStatus.currentData.jobs
		: [], [jobsStatus.isSuccess, jobsStatus.currentData])

	const totalPages = useMemo(() => jobsStatus.isSuccess && jobsStatus.currentData ? jobsStatus.currentData.totalPages : 0, [jobsStatus.isSuccess, jobsStatus.currentData]);

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
				{jobs.map((job) => (
					<Grid key={job.id} item md={3} sm={6} xs={12} padding={1}>
						<JobCard sx={{ height: '100%' }} job={job} />
					</Grid>
				))}
			</Grid>
		);
	}, [jobsStatus.isFetching, jobsStatus.isLoading, jobs]);

	const JobsDisplay = useMemo(
		() => (
			<Stack paddingY={5} spacing={2}>
				{Jobs}
				<Stack direction="row" justifyContent="center">
					<Button disabled={page === 1} onClick={() => setPage(page - 1)}>Prev</Button>
					<Button>{page}</Button>
					<Button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</Button>
				</Stack>
			</Stack>
		),
		[Jobs, jobsStatus.isFetching, jobsStatus.isLoading, page, jobs.length, perPage]
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

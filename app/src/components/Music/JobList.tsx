import { useState, useMemo, useEffect } from 'react';
import { Box, CircularProgress, Grid, Pagination, Typography, Stack, Divider } from '@mui/material';
import { useJobsQuery } from '../../api/music';
import JobCard from './JobCard';

const JobList = () => {
	const [args, setArgs] = useState<PageBody>({
		page: 1,
		perPage: 5,
	});
	const [jobs, setJobs] = useState<Job[]>([]);
	const [totalPages, setTotalPages] = useState(1);

	const jobsStatus = useJobsQuery(args);

	const renderJobs = useMemo(() => {
		if (jobsStatus.isLoading || jobsStatus.isFetching) {
			return (
				<Stack justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (jobs.length === 0) {
			return <Stack justifyContent="center">No Jobs</Stack>;
		}
		return (
			<Grid container spacing={2}>
				{jobs.map((job) => (
					<Grid item xs={12} sm={6} md={4} xl={2}>
						<JobCard {...job} />
					</Grid>
				))}
			</Grid>
		);
	}, [jobs, jobsStatus.isFetching, jobsStatus.isLoading]);

	useEffect(() => {
		if (jobsStatus.isSuccess && jobsStatus.currentData) {
			const { jobs, totalPages } = jobsStatus.currentData;
			setJobs(jobs);
			setTotalPages(totalPages);
		}
	}, [jobsStatus.currentData, jobsStatus.isSuccess]);

	return useMemo(
		() => (
			<Box>
				<Stack
					direction="row"
					justifyContent={{
						xs: 'center',
						sm: 'space-between',
					}}
					spacing={2}
					flexWrap="wrap"
					paddingY={2}
				>
					<Typography variant="h4">Jobs</Typography>
					<Pagination
						page={args.page}
						count={totalPages}
						color="primary"
						shape="rounded"
						onChange={(e, page) => setArgs((value) => ({ ...value, page }))}
					/>
				</Stack>
				<Divider />
				<Box paddingY={2}>{renderJobs}</Box>
			</Box>
		),
		[args.page, renderJobs, totalPages]
	);
};

export default JobList;

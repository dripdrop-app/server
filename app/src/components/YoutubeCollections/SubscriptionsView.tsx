import { useMemo, useReducer } from 'react';
import { Stack, Box, Grid, Paper, Skeleton } from '@mui/material';
import { useYoutubeSubscriptionsQuery } from '../../api';
import SubscriptionCard from './SubscriptionCard';
import Paginator from '../Paginator';

const initialState: PageState = {
	page: 1,
	perPage: 50,
};

const reducer = (state = initialState, action: Partial<PageState>) => {
	return { ...state, ...action };
};

const SubscriptionsView = () => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const subscriptionsStatus = useYoutubeSubscriptionsQuery(filterState);

	const totalSubscriptions = useMemo(
		() =>
			subscriptionsStatus.isSuccess && subscriptionsStatus.currentData
				? subscriptionsStatus.currentData.totalSubscriptions
				: 0,
		[subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]
	);

	const Subscriptions = useMemo(() => {
		if (subscriptionsStatus.currentData && !subscriptionsStatus.isFetching) {
			const { subscriptions } = subscriptionsStatus.currentData;
			return subscriptions.map((subscription) => (
				<Grid key={`grid-${subscription.id}`} item md={2.93} sm={5.93} xs={12}>
					<SubscriptionCard sx={{ height: '100%' }} subscription={subscription} />
				</Grid>
			));
		}
		return Array(50)
			.fill(0)
			.map((v, i) => (
				<Grid key={`grid-${i}`} item md={2.93} sm={5.93} xs={12}>
					<Skeleton height="30vh" variant="rectangular" />
				</Grid>
			));
	}, [subscriptionsStatus.currentData, subscriptionsStatus.isFetching]);

	const Pager = useMemo(
		() => (
			<Paginator
				page={filterState.page}
				pageCount={Math.ceil(totalSubscriptions / filterState.perPage)}
				isFetching={subscriptionsStatus.isFetching}
				onChange={(newPage) => filterDispatch({ page: newPage })}
			/>
		),
		[filterState.page, filterState.perPage, subscriptionsStatus.isFetching, totalSubscriptions]
	);

	return useMemo(
		() => (
			<Stack spacing={2} paddingY={2}>
				<Grid container gap={1}>
					{Subscriptions}
				</Grid>
				<Box display={{ md: 'none' }}>
					<Stack direction="row" justifyContent="center">
						{Pager}
					</Stack>
				</Box>
				<Box display={{ xs: 'none', md: 'block' }}>
					<Paper sx={{ width: '100vw', position: 'fixed', left: 0, bottom: 0, padding: 2 }}>
						<Stack direction="row" justifyContent="center">
							{Pager}
						</Stack>
					</Paper>
				</Box>
			</Stack>
		),
		[Pager, Subscriptions]
	);
};

export default SubscriptionsView;

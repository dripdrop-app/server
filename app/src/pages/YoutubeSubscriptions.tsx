import { useEffect, useMemo, useReducer, useState } from 'react';
import { Container, Stack, Typography } from '@mui/material';
import { useYoutubeSubscriptionsQuery } from '../api';
import SubscriptionCard from '../components/Youtube/SubscriptionCard';
import CustomGrid from '../components/Youtube/CustomGrid';
import YoutubePage from '../components/Youtube/YoutubePage';

const initialState: PageState = {
	page: 1,
	perPage: 50,
};

const reducer = (state = initialState, action: Partial<PageState>) => {
	return { ...state, ...action };
};

const YoutubeSubscriptions = () => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [subscriptions, setSubscriptions] = useState<YoutubeSubscription[]>([]);

	const subscriptionsStatus = useYoutubeSubscriptionsQuery(filterState);

	useEffect(() => {
		if (subscriptionsStatus.isSuccess && subscriptionsStatus.currentData) {
			const newSubscriptions = subscriptionsStatus.currentData.subscriptions;
			setSubscriptions((subscriptions) => [...subscriptions, ...newSubscriptions]);
		}
	}, [subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]);

	const SubscriptionsView = useMemo(
		() => (
			<Stack spacing={2} paddingY={2}>
				<CustomGrid
					items={subscriptions}
					itemKey={(subscription) => subscription.id}
					renderItem={(subscription) => <SubscriptionCard sx={{ height: '100%' }} subscription={subscription} />}
					perPage={filterState.perPage}
					isFetching={subscriptionsStatus.isFetching}
					fetchMore={() => {
						if (
							subscriptionsStatus.isSuccess &&
							subscriptionsStatus.currentData &&
							subscriptionsStatus.currentData.subscriptions.length === filterState.perPage
						) {
							filterDispatch({ page: filterState.page + 1 });
						}
					}}
				/>
			</Stack>
		),
		[
			filterState.page,
			filterState.perPage,
			subscriptions,
			subscriptionsStatus.currentData,
			subscriptionsStatus.isFetching,
			subscriptionsStatus.isSuccess,
		]
	);

	return useMemo(
		() => (
			<Container>
				<Stack paddingY={2}>
					<Typography variant="h3">Youtube Subscriptions</Typography>
					<YoutubePage render={() => <Stack paddingY={2}>{SubscriptionsView}</Stack>} />
				</Stack>
			</Container>
		),
		[SubscriptionsView]
	);
};

export default YoutubeSubscriptions;

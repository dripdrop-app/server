import { useEffect, useMemo, useReducer, useState } from 'react';
import { Container, Stack, Typography } from '@mui/material';
import { useYoutubeSubscriptionsQuery } from '../api/youtube';
import SubscriptionCard from '../components/Youtube/Content/SubscriptionCard';
import InfiniteScroll from '../components/InfiniteScroll';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';

const initialState: PageState = {
	page: 1,
	perPage: 48,
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
				<InfiniteScroll
					items={subscriptions}
					renderItem={(subscription) => (
						<SubscriptionCard
							key={'subscription' + subscription.id}
							sx={{ height: '100%' }}
							subscription={subscription}
						/>
					)}
					onEndReached={() => {
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
			subscriptionsStatus.isSuccess,
		]
	);

	return useMemo(
		() => (
			<Container>
				<Stack>
					<Typography variant="h3">Youtube Subscriptions</Typography>
					<YoutubePage>
						<Stack paddingY={2}>{SubscriptionsView}</Stack>
					</YoutubePage>
				</Stack>
			</Container>
		),
		[SubscriptionsView]
	);
};

export default YoutubeSubscriptions;

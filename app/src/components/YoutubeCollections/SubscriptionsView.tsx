import { useEffect, useMemo, useReducer, useState } from 'react';
import { Stack } from '@mui/material';
import { useYoutubeSubscriptionsQuery } from '../../api';
import SubscriptionCard from './SubscriptionCard';
import CustomGrid from './CustomGrid';

const initialState: PageState = {
	page: 1,
	perPage: 50,
};

const reducer = (state = initialState, action: Partial<PageState>) => {
	return { ...state, ...action };
};

const SubscriptionsView = () => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const [subscriptions, setSubscriptions] = useState<YoutubeSubscription[]>([]);

	const subscriptionsStatus = useYoutubeSubscriptionsQuery(filterState);

	useEffect(() => {
		if (subscriptionsStatus.isSuccess && subscriptionsStatus.currentData) {
			const newSubscriptions = subscriptionsStatus.currentData.subscriptions;
			setSubscriptions((subscriptions) => [...subscriptions, ...newSubscriptions]);
		}
	}, [subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]);

	return useMemo(
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
};

export default SubscriptionsView;

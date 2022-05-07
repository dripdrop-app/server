import React, { useEffect, useMemo, useState } from 'react';
import { isEqual } from 'lodash';
import { useYoutubeSubscriptionsQuery } from '../../../api/youtube';

interface YoutubeSubscriptionsPageProps extends YoutubeSubscriptionBody {
	renderLoadingItem: () => JSX.Element;
	renderItem: (subscription: YoutubeSubscription, index: number) => JSX.Element;
	onLoading?: (page: number) => void;
	onLoaded?: (page: number, subscriptions: YoutubeSubscription[]) => void;
}

const YoutubeSubscriptionsPage = (props: YoutubeSubscriptionsPageProps) => {
	const { renderItem, renderLoadingItem, onLoaded, onLoading } = props;
	const [args, setArgs] = useState<YoutubeSubscriptionBody>({
		page: props.page,
		perPage: props.perPage,
	});

	const subscriptionsStatus = useYoutubeSubscriptionsQuery(args);

	const subscriptions = useMemo(
		() =>
			subscriptionsStatus.isSuccess && subscriptionsStatus.currentData
				? subscriptionsStatus.currentData.subscriptions
				: [],
		[subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]
	);

	const itemsToRender = useMemo(() => {
		if (subscriptionsStatus.isLoading) {
			return Array(props.perPage)
				.fill(0)
				.map((v, i) => <React.Fragment key={`loading-${args.page}-${i}`}>{renderLoadingItem()}</React.Fragment>);
		}

		return subscriptions.map((subscription, i) => (
			<React.Fragment key={`item-${args.page}-${i}`}>{renderItem(subscription, i)}</React.Fragment>
		));
	}, [subscriptionsStatus.isLoading, subscriptions, props.perPage, args.page, renderLoadingItem, renderItem]);

	useEffect(() => {
		if (onLoaded && subscriptionsStatus.isSuccess && subscriptionsStatus.currentData) {
			onLoaded(args.page, subscriptionsStatus.currentData.subscriptions);
		}
	}, [args.page, onLoaded, subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]);

	useEffect(() => {
		if (onLoading && (subscriptionsStatus.isLoading || subscriptionsStatus.isFetching)) {
			onLoading(args.page);
		}
	}, [args.page, onLoading, subscriptionsStatus.isFetching, subscriptionsStatus.isLoading]);

	useEffect(() => {
		const selectedProps = {
			page: props.page,
			perPage: props.perPage,
		};
		if (!isEqual(selectedProps, args)) {
			setArgs(selectedProps);
		}
	}, [args, props]);

	return <React.Fragment>{itemsToRender}</React.Fragment>;
};

export default YoutubeSubscriptionsPage;
